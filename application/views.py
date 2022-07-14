from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext as _

from application import forms
from application.models import Application, ApplicationTypeConfig, ApplicationLog
from user.mixins import LoginRequiredMixin


class ApplicationHome(LoginRequiredMixin, TemplateView):
    template_name = 'application_home.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_organizer():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_applications = {app.type_id: app for app in Application.objects.filter(user=self.request.user)}
        application_types = ApplicationTypeConfig.objects.filter(public=True)
        accepted_application = None
        for application_type in application_types:
            application_type.user_instance = user_applications.get(application_type.id, None)
            if application_type.user_instance is not None and application_type.user_instance.confirmed():
                accepted_application = application_type.user_instance
        context.update({'user_applications': user_applications.values(), 'accepted_application': accepted_application,
                        'application_types': application_types})
        return context


class ApplicationApplyTemplate(TemplateView):
    template_name = 'application_form.html'
    public = True

    def get_form(self):
        application_type = self.kwargs.get('type').lower().title()
        ApplicationForm = getattr(forms, application_type + 'Form', None)
        if ApplicationForm is None:
            raise Http404()
        return ApplicationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_type = get_object_or_404(ApplicationTypeConfig, name__iexact=kwargs.get('type').lower(),
                                             public=self.public)
        ApplicationForm = self.get_form()
        context.update({'edit': False, 'form': ApplicationForm(), 'application_type': application_type})
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        ApplicationForm = self.get_form()
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                if not self.public:
                    raise Application.DoesNotExist()
                Application.objects.get(user=request.user, type__name__iexact=kwargs.get('type').lower())
            except Application.DoesNotExist:
                instance = form.save(commit=False)
                if self.public:
                    instance.user = request.user
                instance.type_id = context['application_type'].id
                with transaction.atomic():
                    instance.save()
                    form.save_files(instance=instance)
            except Application.MultipleObjectsReturned:
                pass
            messages.success(request, _('Applied successfully!'))
            return redirect('apply_home')
        context.update({'form': form})
        return self.render_to_response(context)


class ApplicationApply(LoginRequiredMixin, ApplicationApplyTemplate):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_organizer():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ApplicationApplyPrivate(ApplicationApplyTemplate):
    public = False

    def dispatch(self, request, *args, **kwargs):
        application_type = get_object_or_404(ApplicationTypeConfig, name__iexact=kwargs.get('type').lower(),
                                             public=self.public)
        if not application_type.token_is_valid(kwargs.get('token')):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class ApplicationEdit(LoginRequiredMixin, TemplateView):
    template_name = 'application_form.html'

    def get_form(self):
        application_type = self.kwargs.get('type').lower().title()
        ApplicationForm = getattr(forms, application_type + 'Form', None)
        if ApplicationForm is None:
            raise Http404(_('Type not active'))
        return ApplicationForm

    def get_application(self, application_type):
        application = get_object_or_404(Application, uuid=self.kwargs.get('uuid'))
        if not self.request.user.is_organizer() and self.request.user != application.user:
            raise PermissionDenied()
        if application.type != application_type:
            raise Http404
        return application

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_type = get_object_or_404(ApplicationTypeConfig, name__iexact=kwargs.get('type').lower(),
                                             public=True)
        ApplicationForm = self.get_form()
        application = self.get_application(application_type)
        form = ApplicationForm(instance=application)
        if not application.can_edit():
            form.set_read_only()
        context.update({'edit': True, 'form': form, 'full_name': application.get_full_name(),
                        'application_type': application_type})
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        ApplicationForm = self.get_form()
        form = ApplicationForm(request.POST, request.FILES, instance=context['form'].instance)
        if form.is_valid():
            application = form.save(commit=False)
            log = ApplicationLog.create_log(application=form.instance, user=request.user)
            with transaction.atomic():
                files = form.save_files(instance=application)
                if len(files) <= 0:
                    application.save()
                log.set_file_changes(files)
                if len(log.changes) > 0:
                    log.save()
            messages.success(request, _('Edited successfully!'))
            return redirect('edit_application', **kwargs)
        context.update({'form': form})
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
        with transaction.atomic():
            application.save()
            log.save()
        return redirect(next_page)
