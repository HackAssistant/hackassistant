import os
from datetime import timedelta
from io import BytesIO
from zipfile import ZipFile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import Error, IntegrityError
from django.db.models import Q, Count, F
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.emails import EmailList
from app.mixins import TabsViewMixin
from app.utils import is_installed
from application import forms
from application.mixins import ApplicationPermissionRequiredMixin
from application.models import Application, FileField, ApplicationLog, ApplicationTypeConfig, PromotionalCode
from review.emails import get_invitation_or_waitlist_email
from review.filters import ApplicationTableFilter, ApplicationTableFilterWithPromotion
from review.forms import CommentForm, DubiousApplicationForm
from review.models import Vote, FileReview, CommentReaction
from review.tables import ApplicationTable, ApplicationInviteTable
from user.mixins import IsOrganizerMixin
from user.models import BlockedUser


class ReviewApplicationTabsMixin(TabsViewMixin):
    def get_review_application(self, application_type):
        max_votes_to_app = getattr(settings, 'MAX_VOTES_TO_APP', 50)
        return Application.objects.actual().filter(type__name__iexact=application_type,
                                                   status=Application.STATUS_PENDING) \
            .exclude(Q(vote__user_id=self.request.user.id) | Q(user_id=self.request.user.id)) \
            .filter(submission_date__lte=timezone.now() - timedelta(hours=2)) \
            .annotate(count=Count('vote__calculated_vote')) \
            .filter(count__lte=max_votes_to_app) \
            .order_by('count', 'submission_date') \
            .first()

    def get_current_tabs(self, **kwargs):
        tabs = []
        active_type = self.request.GET.get('type', 'Hacker')
        for app_type in ApplicationTypeConfig.objects.all().order_by('pk'):
            page_url = reverse('application_list')
            if app_type.vote_enabled() and (self.request.user.has_perm('can_review_application') or
                                            self.request.user.has_perm('can_review_application_%s' %
                                                                       app_type.name.lower())):
                page_url = self.request.path
            url = '%s?type=%s' % (page_url, app_type.name)
            tabs.append((app_type.name, url, app_type.vote_enabled() and
                         self.get_review_application(app_type.name) is not None, active_type == app_type.name))
        return tabs


class ApplicationList(IsOrganizerMixin, ReviewApplicationTabsMixin, SingleTableMixin, FilterView):
    template_name = 'application_list.html'
    table_class = ApplicationTable
    table_pagination = {'per_page': 50}
    filterset_class = ApplicationTableFilter

    def get_table(self, **kwargs):
        permission_slip = self.request.GET.get('user__under_age', '') == 'true'
        return super().get_table(promotional_code=PromotionalCode.active(), slip=permission_slip, **kwargs)

    def get_filterset_class(self):
        if PromotionalCode.active():
            return ApplicationTableFilterWithPromotion
        return super().get_filterset_class()

    def get_application_type(self):
        return self.request.GET.get('type', 'Hacker')

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)
        filterset.form.initial = {'type': self.get_application_type()}
        return filterset

    def get_queryset(self):
        return self.table_class.get_queryset(Application.objects.actual())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            application_type = ApplicationTypeConfig.objects.get(name=self.get_application_type())
            context.update({'application_type': application_type})
        except ApplicationTypeConfig.DoesNotExist:
            pass
        dubious = Application.objects.actual().filter(type__name=self.get_application_type()) \
            .filter(Q(status=Application.STATUS_DUBIOUS) | Q(status=Application.STATUS_NEEDS_CHANGE,
                                                             status_update_date__lt=F('last_modified'))).exists()
        blocked = Application.objects.actual().filter(type__name=self.get_application_type(),
                                                      status=Application.STATUS_BLOCKED,
                                                      status_update_date__gt=(timezone.now() -
                                                                              timezone.timedelta(days=3))).exists()
        emails = list(context['object_list'].values_list('user__email', flat=True))
        context.update({'dubious': dubious, 'Application': Application, 'blocked': blocked,
                        'apply_url': self.request.build_absolute_uri(reverse('apply')), 'emails': emails})
        return context


class ApplicationDetail(IsOrganizerMixin, ApplicationPermissionRequiredMixin, TemplateView):
    template_name = 'application_detail.html'
    permission_required = 'application.view_application'

    def get_application_type(self):
        return self.get_application().type.name

    def get_form(self, application_type):
        application_type = application_type.name.lower().title()
        ApplicationForm = getattr(forms, application_type + 'Form', None)
        if ApplicationForm is None:
            raise Http404()
        return ApplicationForm

    def add_friends_details(self, details, application):
        if is_installed('friends'):
            friend_code = application.user.friendscode_set.first()
            if friend_code is not None:
                friends = friend_code.get_members().exclude(pk=friend_code.pk).values_list('user__email', flat=True)
                if len(friends) > 0:
                    details[_('Number of friends')] = len(friends)
                    details[_('Friends list')] = ', '.join(friends)

    def get_details(self, application):
        details = {_('Full Name'): application.user.get_full_name(), _('Status'): application.get_status_display()}
        if application.promotional_code:
            details[_('Promotion')] = application.promotional_code.name
        for name, value in application.form_data.items():
            if isinstance(value, FileField):
                value = value.url
            if isinstance(value, bool):
                value = _('Yes') if value else _('No')
            if isinstance(value, list):
                value = ', '.join(value)
            details[name.replace('_', ' ').lower().title()] = value
        self.add_friends_details(details, application)
        return details

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_application()
        if application is not None:
            details = self.get_details(application)
            ApplicationForm = self.get_form(application.type)
            icons = {name.replace('_', ' ').lower().title(): value
                     for name, value in getattr(ApplicationForm.Meta, 'icon_link', {}).items()}
            comments = application.logs.filter(comment__isnull=False)
            for comment in comments:
                comment.form = CommentForm(instance=comment)
            context.update({'application': application, 'details': details, 'icons': icons,
                            'comment_form': CommentForm(initial={'application': application.get_uuid}),
                            'comments': comments, 'dubious_form': DubiousApplicationForm(),
                            'application_type': application.type.name})
            if application.status == application.STATUS_BLOCKED:
                try:
                    blocked_user = BlockedUser.get_blocked(full_name=application.user.get_full_name(),
                                                           email=application.user.email)
                    context.update({'blocked_user': blocked_user})
                except BlockedUser.DoesNotExist:
                    pass
        return context

    def get_application(self):
        return get_object_or_404(Application, uuid=self.kwargs.get('uuid'))

    def post(self, request, *args, **kwargs):
        application = self.get_application()
        if not application.type.dubious_enabled():
            raise PermissionDenied()
        dubious_form = DubiousApplicationForm(request.POST)
        if dubious_form.is_valid() and application.status in [application.STATUS_DUBIOUS,
                                                              application.STATUS_NEEDS_CHANGE]:
            url, query_params = dubious_form.save(application=application, request=request)
            query_params.update({'next': request.path})
            return redirect(url + '?' + urlencode(query_params))
        context = self.get_context_data()
        context.update({'dubious_form': dubious_form})
        return self.render_to_response(context)


class ApplicationReview(ReviewApplicationTabsMixin, ApplicationDetail):
    permission_required = 'application.can_review_application'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'votes': dict(Vote.VOTES), 'application_type': self.get_application_type()})
        return context

    def get_application_type(self):
        return self.request.GET.get('type', 'Hacker')

    def get_application(self):
        application_type = self.get_application_type()
        return self.get_review_application(application_type)

    def post(self, request, *args, **kwargs):
        skip = request.POST.get('skip', None)
        tech_vote = request.POST.get('tech_vote', None) if skip is None else None
        pers_vote = request.POST.get('pers_vote', None) if skip is None else None
        application_id = request.POST.get('application_id', None)
        try:
            application = Application.objects.get(pk=application_id)
            if not application.type.vote_enabled():
                raise PermissionDenied()
            Vote(application=application, user=request.user, tech=tech_vote, personal=pers_vote).save()
            if skip is None:
                messages.success(request, _('Application voted successfully! :D'))
            else:
                messages.success(request, _('Application skipped! Try to not skip all xD'))
        except Application.DoesNotExist:
            messages.error(request, _('Someone just deleted the application! :('))
        application_type = self.get_application_type()
        return redirect('%s?type=%s' % (reverse('application_review'), application_type))


class CommentSubmit(IsOrganizerMixin, PermissionRequiredMixin, View):
    permission_required = 'application.add_applicationlog'

    def get_permission_required(self):
        log_id = self.kwargs.get('log_id', None)
        if log_id is None:
            return super().get_permission_required()
        return []

    def post(self, request, *args, **kwargs):
        log_id = kwargs.get('log_id', None)
        if log_id is None:
            comment_form = CommentForm(request.POST)
        else:
            log = get_object_or_404(ApplicationLog, id=log_id)
            if log.user != request.user and not request.user.has_perm('application.change_applicationlog'):
                return self.handle_no_permission()
            comment_form = CommentForm(request.POST, instance=log)
        if comment_form.is_valid():
            log = comment_form.save(commit=False)
            if log_id is None:
                log.user = request.user
            log.save()
            log_dict = log.__dict__
            del log_dict['_state']
            return JsonResponse(log_dict)
        return JsonResponse(dict(comment_form.errors), status=400)


class CommentReactionView(IsOrganizerMixin, View):

    def post(self, request, *args, **kwargs):
        action = self.request.POST.get('action', None)
        if action == 'CREATE':
            comment_id = self.request.POST.get('comment', None)
            emoji = self.request.POST.get('emoji', None)
            try:
                reaction = CommentReaction.objects.get_or_create(user=request.user, comment_id=comment_id,
                                                                 emoji=emoji)[0]
            except Exception:
                return JsonResponse({'error': 'Database error'}, status=400)
            return JsonResponse({'reaction_id': reaction.id})
        elif action == 'DELETE':
            reaction_id = self.request.POST.get('reaction_id', None)
            try:
                reaction = CommentReaction.objects.get(id=reaction_id)
                if reaction.user != request.user:
                    raise PermissionDenied()
            except CommentReaction.DoesNotExist:
                raise Http404()
            reaction.delete()
            return JsonResponse({'reaction_id': reaction.id})
        return JsonResponse({}, status=401)


class ApplicationLogs(IsOrganizerMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'application_logs.html'
    permission_required = 'application.view_applicationlog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = get_object_or_404(Application, uuid=self.kwargs.get('uuid'))
        context.update({'application': application, 'logs': application.logs.order_by('-date')})
        return context


class ApplicationListInvite(ApplicationPermissionRequiredMixin, ApplicationList):
    table_class = ApplicationInviteTable
    permission_required = 'application.can_invite_application'

    def get_current_tabs(self, **kwargs):
        return []

    def dispatch(self, request, *args, **kwargs):
        application_type = get_object_or_404(ApplicationTypeConfig, name=self.request.GET.get('type', 'Hacker'))
        if application_type.auto_confirm:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_application_status(application_type):
        return Application.objects.actual().filter(type=application_type).aggregate(
            accepted=Count('uuid', filter=Q(status__in=[Application.STATUS_CONFIRMED, Application.STATUS_ATTENDED])),
            invited=Count('uuid', filter=Q(status__in=[Application.STATUS_INVITED, Application.STATUS_LAST_REMINDER]))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'invite': True, 'application_stats': self.get_application_status(context['application_type'])})
        return context

    def post(self, request, *args, **kwargs):
        selection = request.POST.getlist('select')
        error = 0
        emails = EmailList()
        new_status = request.POST.get('status', Application.STATUS_INVITED)
        status_name = [y for x, y in Application.STATUS if x == new_status][0]
        for application in Application.objects.actual().filter(uuid__in=selection):
            if application.status != new_status:
                log = ApplicationLog(application=application, user=request.user, name=status_name)
                log.changes = {'status': {'old': application.status, 'new': new_status}}
                application.set_status(new_status)
                try:
                    application.save()
                    log.save()
                    emails.add(get_invitation_or_waitlist_email(request, application))
                except Error:
                    error += 1
        emails = emails.send_all()
        if error > 0:
            messages.error(request, _('%s %s, Emails sent: %s, Error: %s') %
                           (status_name, len(selection) - error, emails or 0, error))
        else:
            messages.success(request, _('%s: %s, Emails sent: %s' % (status_name, len(selection), emails or 0)))
        return redirect(reverse('application_list') + '?type=%s&status=%s' % (self.get_application_type(), new_status))


class FileReviewView(ApplicationPermissionRequiredMixin, TabsViewMixin, TemplateView):
    template_name = 'file_review.html'
    permission_required = 'application.can_review_files'

    def get_current_tabs(self, **kwargs):
        tabs = []
        active_type = self.get_application_type()
        active_field = self.request.GET.get('field', None)
        for application_type in ApplicationTypeConfig.objects.filter(file_review_fields__isnull=False):
            if self.has_permission(application_type=application_type.name):
                for index, file_field in enumerate(application_type.get_file_review_fields()):
                    active = active_type == application_type.name and (file_field == active_field or
                                                                       (active_field is None and index == 0))
                    url = reverse('file_review') + '?type=%s&file=%s' % (application_type.name, file_field)
                    tabs.append(('%s: %s' % (application_type.name, file_field), url, None, active))
        return tabs

    def get_application_type(self):
        return self.request.GET.get('type', 'Hacker')

    def get_file_field(self, application_type):
        return self.request.GET.get('field', application_type.get_file_review_fields()[0])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application_type = get_object_or_404(ApplicationTypeConfig, name=self.get_application_type(),
                                             file_review_fields__isnull=False)
        file_field = self.get_file_field(application_type)
        exclude_kwargs = {file_field + '_share': False}
        application_uuid = FileReview.objects.filter(application__type__name=application_type, field_name=file_field) \
            .values_list('application_id', flat=True)
        application = Application.objects.actual().filter(type_id=application_type.pk) \
            .exclude(uuid__in=application_uuid).distinct().exclude(**exclude_kwargs).first()
        if application is not None:
            context.update({'application': application, 'field': file_field,
                            'download': reverse('application_file', kwargs={'field': file_field,
                                                                            'uuid': application.get_uuid})})
        else:
            context.update({'download': reverse('file_review') + '?type=%s&file=%s&download_all=True' % (
                application_type.name, file_field)})
        return context

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, uuid=request.POST.get('application'))
        field_name = request.POST.get('field')
        accept = request.POST.get('accepted').lower() == 'true'
        try:
            FileReview(application=application, field_name=field_name, accept=accept, user=request.user).save()
        except IntegrityError:
            pass
        if accept:
            messages.success(request, _('File accepted for download!'))
        else:
            messages.success(request, _('File denied for download!'))
        return redirect(reverse('file_review') + '?type=%s&file=%s' % (application.type.name, field_name))

    def get(self, request, *args, **kwargs):
        file = request.GET.get('download_all', False)
        if file:
            application_type = get_object_or_404(ApplicationTypeConfig, name=self.get_application_type(),
                                                 file_review_fields__isnull=False)
            file_field = self.get_file_field(application_type)
            applications = Application.objects.actual().filter(type_id=application_type.pk,
                                                               filereview__field_name=file_field,
                                                               filereview__accept=True)
            s = BytesIO()
            with ZipFile(s, "w") as zip_file:
                for application in applications:
                    try:
                        file_path = settings.MEDIA_ROOT + '/' + application.form_data[file_field]['path']
                    except KeyError:
                        raise SuspiciousOperation('This field does not exist')
                    _, fname = os.path.split(file_path)
                    zip_path = os.path.join("resumes", fname)
                    zip_file.write(file_path, zip_path)
            resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
            resp['Content-Disposition'] = 'attachment; filename=%s_%ss.zip' % (application_type.name, file_field)
            return resp
        return super().get(request, *args, **kwargs)
