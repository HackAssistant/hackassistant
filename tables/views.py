from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin
from django_tables2.export import ExportMixin

from app.mixins import TabsViewMixin
from tables.mixins import TablePermissionRequiredMixin
from user.mixins import IsOrganizerMixin
from tables import tables, filters

MODELS = ['vote', 'reaction']


class TablesHome(IsOrganizerMixin, View):
    def get(self, request, *args, **kwargs):
        final_model = MODELS[0]
        if not request.user.has_perms(['tables.view_table']):
            for model in MODELS:
                if request.user.has_perms(['tables.view_table_%s' % model.lower()]):
                    final_model = model
        return redirect(reverse('model_table', kwargs={'model': final_model}))


class ModelTableView(TablePermissionRequiredMixin, TabsViewMixin, ExportMixin, SingleTableMixin, TemplateView):
    template_name = 'model_table.html'
    permission_required = ['tables.view_table']

    def get_current_tabs(self, **kwargs):
        all_perm = self.request.user.has_perms(self.permission_required)
        return [(item.title() + 's', reverse('model_table', kwargs={'model': item})) for item in MODELS
                if all_perm or self.request.user.has_perms(['tables.view_table_%s' % item.lower()])]

    def get_table_class(self):
        model_name = self.kwargs.get('model', '').lower().title()
        table_class = getattr(tables, model_name + 'Table', None)
        if table_class is None:
            raise Http404()
        return table_class

    def get_table_filter_class(self):
        model_name = self.kwargs.get('model', '').lower().title()
        filter_class = getattr(filters, model_name + 'TableFilter', None)
        return filter_class

    #  Table manages the queryset
    def get_table_kwargs(self):
        table_kwargs = super().get_table_kwargs()
        #  Passing force update to retrieve data from DB to the table
        table_kwargs['force_update'] = self.request.GET.get('force_update', 'false') == 'true'
        filter_class = self.get_table_filter_class()
        #  Passing the filter if any, so that the table can filter the data
        if filter_class is not None:
            table_kwargs['filter_class'] = filter_class
            table_kwargs['request_get'] = self.request.GET
        return table_kwargs

    #  Queryset are handled by Tables itself
    def get_queryset(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.kwargs.get('model', '').lower().title()
        table_class = self.get_table_class()
        context.update({'model_name': model_name, 'updated_time': table_class.get_queryset.get_cache_time()})
        return context
