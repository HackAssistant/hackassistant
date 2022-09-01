from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import Error
from django.db.models import Q, Count, F
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from application import forms
from application.mixins import ApplicationPermissionRequiredMixin
from application.models import Application, FileField, ApplicationLog, ApplicationTypeConfig
from review.filters import ApplicationTableFilter
from review.forms import CommentForm, DubiousApplicationForm
from review.models import Vote
from review.tables import ApplicationTable, ApplicationInviteTable
from user.mixins import IsOrganizerMixin
from user.models import BlockedUser


class ReviewApplicationTabsMixin(TabsViewMixin):
    def get_review_application(self, application_type):
        max_votes_to_app = getattr(settings, 'MAX_VOTES_TO_APP', 50)
        return Application.objects.actual().filter(type__name=application_type, status=Application.STATUS_PENDING) \
            .exclude(Q(vote__user_id=self.request.user.id) | Q(user_id=self.request.user.id)) \
            .filter(submission_date__lte=timezone.now() - timedelta(hours=2)) \
            .annotate(count=Count('vote__calculated_vote')) \
            .filter(count__lte=max_votes_to_app) \
            .order_by('count', 'submission_date') \
            .first()

    def get_current_tabs(self):
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
    table_pagination = {'per_page': 100}
    queryset = Application.objects.actual()
    filterset_class = ApplicationTableFilter

    def get_application_type(self):
        return self.request.GET.get('type', 'Hacker')

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)
        filterset.form.initial = {'type': self.get_application_type()}
        return filterset

    def get_queryset(self):
        return self.table_class.get_queryset(super().get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            application_type = ApplicationTypeConfig.objects.get(name=self.get_application_type())
            context.update({'application_type': application_type})
        except ApplicationTypeConfig.DoesNotExist:
            pass
        dubious = Application.objects.actual().filter(type__name=self.get_application_type())\
            .filter(Q(status=Application.STATUS_DUBIOUS) | Q(status=Application.STATUS_NEEDS_CHANGE,
                                                             status_update_date__lt=F('last_modified'))).exists()
        blocked = Application.objects.actual().filter(type__name=self.get_application_type(),
                                                      status=Application.STATUS_BLOCKED,
                                                      status_update_date__gt=(timezone.now() -
                                                                              timezone.timedelta(days=3))).exists()
        context.update({'dubious': dubious, 'Application': Application, 'blocked': blocked})
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_application()
        if application is not None:
            details = {_('Full Name'): application.user.get_full_name(), _('Status'): application.get_status_display()}
            ApplicationForm = self.get_form(application.type)
            for name, value in application.form_data.items():
                if isinstance(value, FileField):
                    value = value.url
                if isinstance(value, bool):
                    value = _('Yes') if value else _('No')
                if isinstance(value, list):
                    value = ', '.join(value)
                details[name.replace('_', ' ').lower().title()] = value
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
        return ['application.change_applicationlog', ]

    def post(self, request, *args, **kwargs):
        log_id = kwargs.get('log_id', None)
        if log_id is None:
            comment_form = CommentForm(request.POST)
        else:
            log = get_object_or_404(ApplicationLog, id=log_id)
            if log.user != request.user:
                raise PermissionDenied()
            comment_form = CommentForm(request.POST, instance=log)
        if comment_form.is_valid():
            log = comment_form.save(commit=False)
            log.user = request.user
            log.save()
            log_dict = log.__dict__
            del log_dict['_state']
            return JsonResponse(log_dict)
        return JsonResponse(dict(comment_form.errors), status=400)


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

    def get_current_tabs(self):
        return []

    def dispatch(self, request, *args, **kwargs):
        application_type = get_object_or_404(ApplicationTypeConfig, name=self.request.GET.get('type', 'Hacker'))
        if application_type.auto_confirm:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'invite': True})
        return context

    def post(self, request, *args, **kwargs):
        selection = request.POST.getlist('select')
        error = 0
        for application in Application.objects.actual().filter(uuid__in=selection):
            log = ApplicationLog(application=application, user=request.user, name='Invited')
            log.changes = {'status': {'old': application.status, 'new': Application.STATUS_INVITED}}
            application.set_status(Application.STATUS_INVITED)
            try:
                application.save()
                log.save()
            except Error:
                error += 1
        if error > 0:
            messages.error(request, _('Invited %s, Error: %s') % (len(selection) - error, error))
        else:
            messages.success(request, _('Invited: %s' % len(selection)))
        return redirect(reverse('application_list') + '?type=%s&status=%s' % (self.get_application_type(),
                                                                              Application.STATUS_INVITED))
