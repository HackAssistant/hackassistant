from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from application import forms
from application.models import Application, FileField, ApplicationLog, ApplicationTypeConfig
from review.filters import ApplicationTableFilter
from review.forms import CommentForm
from review.tables import ApplicationTable
from user.mixins import IsOrganizerMixin


class ReviewApplicationTabsMixin(TabsViewMixin):
    def get_current_tabs(self):
        tabs = []
        active_type = self.request.GET.get('type', 'Hacker')
        for name in ApplicationTypeConfig.objects.all().values_list('name', flat=True):
            url = '%s?type=%s' % (reverse('application_list'), name)
            tabs.append((name, url, False, active_type == name))
        return tabs


class ApplicationList(IsOrganizerMixin, ReviewApplicationTabsMixin, SingleTableMixin, FilterView):
    template_name = 'application_list.html'
    table_class = ApplicationTable
    table_pagination = {'per_page': 100}
    queryset = Application.objects.all()
    filterset_class = ApplicationTableFilter

    def get_filterset(self, filterset_class):
        filterset = super().get_filterset(filterset_class)
        filterset.form.initial = {'type': self.request.GET.get('type', 'Hacker')}
        return filterset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            application_type = ApplicationTypeConfig.objects.get(name=self.request.GET.get('type', 'Hacker'))
            context.update({'application_type': application_type})
        except ApplicationTypeConfig.DoesNotExist:
            pass
        return context


class ApplicationDetail(IsOrganizerMixin, TemplateView):
    template_name = 'application_detail.html'

    def get_form(self, application_type):
        application_type = application_type.name.lower().title()
        ApplicationForm = getattr(forms, application_type + 'Form', None)
        if ApplicationForm is None:
            raise Http404()
        return ApplicationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.get_application()
        details = {'Status': application.get_status_display()}
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
            if comment.user == self.request.user:
                comment.form = CommentForm(instance=comment)
        context.update({'application': application, 'details': details, 'icons': icons,
                        'comment_form': CommentForm(initial={'application': application.get_uuid}),
                        'comments': comments})
        return context

    def get_application(self):
        return get_object_or_404(Application, uuid=self.kwargs.get('uuid'))


class CommentSubmit(IsOrganizerMixin, View):
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
