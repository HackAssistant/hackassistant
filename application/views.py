from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from app.mixins import TabsViewMixin
from app.utils import is_installed
from application import forms
from application.emails import send_email_to_blocked_admins
from application.models import Application, ApplicationTypeConfig, ApplicationLog, Edition, DraftApplication
from user.emails import send_verification_email
from user.forms import UserProfileForm, RecaptchaForm
from user.mixins import LoginRequiredMixin
from user.models import BlockedUser


class ApplicationHome(LoginRequiredMixin, TabsViewMixin, TemplateView):
    template_name = 'application_home.html'

    def get_current_tabs(self, **kwargs):
        tabs = [("Applications", reverse("apply_home"))]
        edition = Edition.get_default_edition()
        if is_installed("friends") and Application.objects.filter(type__name="Hacker", user=self.request.user,
                                                                  edition=edition).exists():
            tabs.append(("Friends", reverse("join_friends")))
        return tabs if len(tabs) > 1 else []

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_organizer():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_user_applications_grouped(self, user_applications):
        result = {}
        for user_application in user_applications:
            status = user_application.get_public_status() if user_application.confirmed() else 'default'
            aux = result.get(status, [])
            aux.append(user_application)
            result[status] = aux
        return result

    def get_application_type_left(self, user_applications):
        user_types = [item.type_id for item in user_applications]
        return ApplicationTypeConfig.objects.filter(hidden=False).exclude(id__in=user_types)\
            .exclude(end_application_date__lt=timezone.now())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_applications = Application.objects.actual().filter(user=self.request.user)
        user_applications_grouped = self.get_user_applications_grouped(user_applications)
        apply_types = self.get_application_type_left(user_applications)
        context.update({'user_applications': user_applications, 'user_applications_grouped': user_applications_grouped,
                        'apply_types': apply_types, 'Application': Application})
        return context


class ApplicationApply(TemplateView):
    template_name = 'application_form.html'
    public = True

    def dispatch(self, request, *args, **kwargs):
        app_type = self.request.GET.get('type', None)
        this_edition = Edition.get_default_edition()
        try:
            application_type = get_object_or_404(ApplicationTypeConfig,
                                                 name__iexact=self.request.GET.get('type', 'Hacker').lower(),
                                                 token=self.request.GET.get('token', None))
        except ValidationError:
            raise Http404
        if request.user.is_authenticated and request.user.email_verified:
            try:
                Application.objects.get(user=request.user, type__name=app_type, edition=this_edition)
                messages.warning(request, _('You have already applied!'))
                return redirect(reverse('apply_home'))
            except Application.DoesNotExist:
                pass
        elif application_type.only_authenticated:
            return redirect(reverse('login') + '?' + urlencode({'next': request.get_full_path()}))
        kwargs['application_type'] = application_type
        return super().dispatch(request, *args, **kwargs)

    @classmethod
    def get_form_class(cls, type_name):
        application_type = type_name.lower().title()
        ApplicationForm = getattr(forms, application_type + 'Form', None)
        if ApplicationForm is None:
            raise Http404()
        return ApplicationForm

    def update_from_last_edition_application(self, application_type, initial_data):
        last_edition = Edition.get_last_edition()
        try:
            last_edition_app = Application.objects.get(edition_id=last_edition, type=application_type,
                                                       user=self.request.user)
            initial_data.update({key: value for key, value in last_edition_app.form_data.items()
                                 if isinstance(value, str)})
        except Application.DoesNotExist:
            pass

    def update_from_draft_application(self, initial_data):
        try:
            draft = DraftApplication.objects.get(user_id=self.request.user.id)
            initial_data.update(draft.form_data)
        except DraftApplication.DoesNotExist:
            pass

    def get_forms(self, application_type, application_form_class):
        initial_data = {key: value for key, value in self.request.GET.dict().items()
                        if key not in application_form_class.exclude_save}
        if self.request.user.is_authenticated:
            self.update_from_last_edition_application(application_type, initial_data)
            self.update_from_draft_application(initial_data)
        app_form_kwargs = {'initial': initial_data}
        user_form_kwargs = app_form_kwargs.copy()
        if self.request.user.is_authenticated:
            user_form_kwargs['instance'] = self.request.user
        recaptcha_form = None
        if not self.request.user.is_authenticated and getattr(settings, 'RECAPTCHA_REGISTER', False) and \
                RecaptchaForm.active():
            recaptcha_form = RecaptchaForm(request=self.request)
        return application_form_class(**app_form_kwargs), UserProfileForm(**user_form_kwargs), recaptcha_form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_type = kwargs.get('application_type')

        application_form_class = self.get_form_class(type_name=self.request.GET.get('type', 'Hacker'))
        application_form, user_form, recaptcha_form = self.get_forms(application_type, application_form_class)

        context.update({'edit': False, 'application_form': application_form, 'application_type': application_type,
                        'user_form': user_form, 'recaptcha_form': recaptcha_form})
        return context

    def block_application(self, user, application):
        blocked_user = BlockedUser.get_blocked(full_name=user.get_full_name(), email=user.email)
        application.status = Application.STATUS_BLOCKED
        User = get_user_model()
        perms = ['can_review_blocked_application', 'can_review_blocked_application_%s' %
                 application.type.name.lower()]
        users_emails = User.get_users_with_permissions(perms).values_list('email', flat=True)
        send_email_to_blocked_admins(self.request, users_emails, application=application, blocked_user=blocked_user)

    def save_application(self, form, app_type, user):
        try:
            if not self.public:
                raise Application.DoesNotExist()
            Application.objects.get(user=user, type_id=app_type.pk, edition=Edition.get_default_edition())
        except Application.DoesNotExist:
            instance = form.save(commit=False)
            instance.user = user
            instance.type_id = app_type.pk
            if app_type.auto_confirm:
                instance.status = Application.STATUS_CONFIRMED
            if app_type.blocklist:
                try:
                    self.block_application(user, application=instance)
                except BlockedUser.DoesNotExist:
                    pass
            with transaction.atomic():
                instance.save()
                form.save_files(instance=instance)
        except Application.MultipleObjectsReturned:
            pass

    def forms_are_valid(self, user_form, application_form, context):
        if not self.request.user.is_authenticated and getattr(settings, 'RECAPTCHA_REGISTER', False) \
                and RecaptchaForm.active():
            recaptcha_form = RecaptchaForm(self.request.POST, request=self.request)
            if not recaptcha_form.is_valid():
                context.update({'recaptcha_form': recaptcha_form})
                return False
        return user_form.is_valid() and application_form.is_valid()

    def save_user(self, form, create_active_user):
        user = form.save(commit=False)
        user_registered = False
        if user._state.db is None and not create_active_user:
            user.is_active = False
        elif user._state.db is None:
            user_registered = True
        user.save()
        return user, user_registered

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        application_type = context.get('application_type')
        if application_type.closed():
            raise PermissionDenied('Applications are closed')
        application_form_class = self.get_form_class(type_name=self.request.GET.get('type', 'Hacker'))
        application_form = application_form_class(request.POST, request.FILES)
        user_form_kwargs = {}
        if self.request.user.is_authenticated:
            user_form_kwargs['instance'] = self.request.user
        user_form = UserProfileForm(request.POST, **user_form_kwargs)
        if self.forms_are_valid(user_form, application_form, context):
            user, registered = self.save_user(user_form, application_type.create_user)
            self.save_application(form=application_form, app_type=application_type, user=user)
            return self.success_response(application_type, registered, user)
        context.update({'application_form': application_form, 'user_form': user_form})
        return self.render_to_response(context)

    def success_response(self, application_type, registered, user):
        messages.success(self.request, _('Applied successfully!'))
        if application_type.create_user and registered:
            send_verification_email(request=self.request, user=user)
            token = PasswordResetTokenGenerator().make_token(user)
            uuid = user.get_encoded_pk()
            return redirect(reverse('password_reset', kwargs={'uid': uuid, 'token': token}))
        elif not application_type.create_user and not self.request.user.is_authenticated:
            return render(self.request, 'application_success.html', {'application_type': application_type})
        return redirect('apply_home')


class ApplicationEdit(LoginRequiredMixin, TemplateView):
    template_name = 'application_form.html'

    def get_form(self, application_type):
        ApplicationForm = getattr(forms, application_type.name.lower().title() + 'Form', None)
        if ApplicationForm is None:
            raise Http404(_('Type not active'))
        return ApplicationForm

    def get_application(self):
        application = get_object_or_404(Application, uuid=self.kwargs.get('uuid'))
        if self.request.user != application.user and not (self.request.user.is_organizer() and
                                                          (self.request.user.has_perm('change_application') or
                                                           self.request.user.has_perm('change_application_%s' %
                                                                                      application.type.name.lower()))):
            raise PermissionDenied()
        return application

    def application_can_edit(self, application, application_type):
        return self.request.user.is_organizer() or (application.can_edit() and application_type.active())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_application()
        application_type = application.type
        ApplicationForm = self.get_form(application_type)
        application_form = ApplicationForm(instance=application)
        user_form = UserProfileForm(instance=application.user)
        if not self.application_can_edit(application, application_type):
            application_form.set_read_only()
            user_form.set_read_only()
        context.update({'edit': True, 'application_form': application_form, 'full_name': application.get_full_name(),
                        'application_type': application_type, 'user_form': user_form})
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        ApplicationForm = self.get_form(context.get('application_type'))
        user_form = UserProfileForm(request.POST, instance=context['user_form'].instance)
        application_form = ApplicationForm(request.POST, request.FILES, instance=context['application_form'].instance)
        if user_form.is_valid() and application_form.is_valid():
            user_form.save()
            application = application_form.save(commit=False)
            log = ApplicationLog.create_log(application=application_form.instance, user=request.user)
            with transaction.atomic():
                files = application_form.save_files(instance=application)
                if len(files) <= 0:
                    application.save()
                log.set_file_changes(files)
                if len(log.changes) > 0:
                    log.comment = self.request.POST.get('comment_applicationlog', '')[:250]
                    log.save()
            messages.success(request, _('Edited successfully!'))
            return redirect('edit_application', **kwargs)
        context.update({'application_form': application_form, 'user_form': user_form})
        return self.render_to_response(context)


class ApplicationFilePreview(LoginRequiredMixin, TemplateView):
    template_name = 'preview_file.html'

    def get_application(self, kwargs):
        application = get_object_or_404(Application, uuid=kwargs.get('uuid'))
        if not self.request.user.is_organizer() and self.request.user != application.user:
            raise PermissionDenied()
        return application

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_application(kwargs)
        field = application.form_data.get(kwargs.get('field'), None)
        if not isinstance(field, dict) or not field.get('type', None) == 'file':
            raise Http404
        context.update({'field': field, 'application': application, 'field_name': kwargs.get('field'),
                        'download': reverse('application_file', kwargs={
                            'field': self.kwargs.get('field'), 'uuid': self.kwargs.get('uuid')})})
        return context

    def render_to_response(self, context, **response_kwargs):
        if not context['field']['path'].endswith('.pdf'):
            return redirect(context['download'])
        return super().render_to_response(context, **response_kwargs)


class ApplicationFile(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        application = get_object_or_404(Application, uuid=kwargs.get('uuid'))
        if not request.user.is_organizer() and request.user != application.user:
            raise PermissionDenied()
        field = application.form_data.get(kwargs.get('field'), None)
        if isinstance(field, dict) and field.get('type', None) == 'file':
            fs = FileSystemStorage()
            file = fs.open(field.get('path'))
            return HttpResponse(file, content_type='application/%s' % field.get('path').split('.')[-1])
        raise Http404()


class ApplicationChangeStatus(LoginRequiredMixin, View):
    def get_application(self, kwargs):
        application = get_object_or_404(Application, uuid=kwargs.get('uuid'))
        if not self.request.user.is_organizer() and self.request.user != application.user:
            raise PermissionDenied()
        return application

    def get(self, request, **kwargs):
        application = self.get_application(kwargs)
        new_status = kwargs.get('status')
        next_page = self.request.GET.get('next', None) or reverse('home')
        if next_page[0] != '/':
            next_page = reverse('home')
        status_dict = {x: y for (x, y) in application.STATUS}
        if new_status not in status_dict.keys():
            raise Http404()
        if not request.user.is_organizer() and new_status != application.STATUS_CANCELLED:
            if new_status != application.STATUS_CONFIRMED or application.status not in \
                    [application.STATUS_INVITED, application.STATUS_LAST_REMINDER]:
                raise PermissionDenied()
        application.set_status(new_status)
        log = ApplicationLog.create_log(application=application, user=request.user, name=status_dict.get(new_status))
        if request.user.is_organizer:
            log.comment = self.request.GET.get('comment', '')[:250]
        with transaction.atomic():
            application.save()
            log.save()
            if new_status == Application.STATUS_ATTENDED:
                group = Group.objects.get_or_create(application.type.name)
                group.user_set.add(application.user)
            if new_status == application.STATUS_CONFIRMED:
                Application.objects.actual().exclude(uuid=application.get_uuid)\
                    .filter(user=application.user, type__compatible_with_others=False)\
                    .update(status=Application.STATUS_CANCELLED, status_update_date=timezone.now())
        return redirect(next_page)


class SaveDraftApplication(LoginRequiredMixin, View):
    def get_data(self):
        data = self.request.POST.dict()
        del data['csrfmiddlewaretoken']
        for key, value in self.request.POST.dict().items():
            if key[-2:] == '[]':
                del data[key]
                data[key[:-2]] = self.request.POST.getlist(key)
        return data

    def post(self, request, **kwargs):
        data = self.get_data()
        draft, created = DraftApplication.objects.get_or_create(user_id=self.request.user.id,
                                                                defaults={'form_data': data})
        if not created:
            draft.form_data = data
            draft.save()
        return HttpResponse('OK!')
