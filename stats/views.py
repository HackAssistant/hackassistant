from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from app.mixins import TabsViewMixin
from application.models import Application, Edition
from stats import filters
from stats import stats
from stats.utils import cache_stats
from user.mixins import IsOrganizerMixin
from user.models import User


MODELS = ['user', 'application']


class StatsHome(IsOrganizerMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('stats', kwargs={'model': MODELS[0]}))


class StatsMixin:
    def get_filter_class(self, model_name):
        filter_class = getattr(filters, model_name + 'StatsFilter', None)
        if filter_class is None:
            raise Http404()
        return filter_class

    def get_stats_class(self, model_name):
        stats_class = getattr(stats, model_name + 'Stats', None)
        if stats_class is None:
            raise Http404()
        return stats_class


class StatsView(IsOrganizerMixin, TabsViewMixin, StatsMixin, TemplateView):
    template_name = 'stats.html'

    def get_current_tabs(self, **kwargs):
        return [(item.title() + 's', reverse('stats', kwargs={'model': item})) for item in MODELS]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.kwargs.get('model', '').lower().title()
        filter_class = self.get_filter_class(model_name)
        stats_class = self.get_stats_class(model_name)
        context.update({'filter': filter_class(), 'name': model_name, 'stats': stats_class()})
        return context


def get_application_queryset():
    edition = Edition.get_default_edition()
    return Application.objects.filter(edition=edition)


class StatsDataView(IsOrganizerMixin, StatsMixin, View):
    queryset = {'user': User.objects.filter(is_active=True), 'application': get_application_queryset}

    @cache_stats
    def get_queryset(self, model_name):
        queryset = self.queryset.get(model_name.lower())
        if callable(queryset):
            queryset = queryset()
        return list(queryset)

    def get_stats(self, model_name, filter_class, stats_class):
        model_list = self.get_queryset(model_name, force_update=self.request.GET.get('update_cache', None) is not None)
        model_filter = filter_class(self.request.GET)
        if model_filter.form.is_valid():
            model_list = model_filter.filter_list(model_list)
            data = stats_class().to_json(model_list)
            data['updated_time'] = self.get_queryset.get_cache_time(model_name)
            data['total'] = len(model_list)
            return data
        return {}

    def get(self, request, *args, **kwargs):
        model_name = kwargs.get('model', '').lower().title()
        filter_class = self.get_filter_class(model_name)
        stats_class = self.get_stats_class(model_name)
        data = self.get_stats(model_name, filter_class, stats_class)
        return JsonResponse(data)
