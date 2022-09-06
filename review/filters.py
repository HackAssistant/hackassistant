import django_filters as filters
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from application.models import Application


class ApplicationTableFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'search', 'space': 8}, {'name': 'user__under_age', 'space': 2},
                   {'name': 'promotional_code', 'space': 2}, {'name': 'status', 'space': 12}, {'name': 'type'}]},
    }


class ApplicationTableFilter(filters.FilterSet):
    search = filters.CharFilter(method='search_filter', label=_('Search'))
    status = filters.MultipleChoiceFilter(choices=Application.STATUS,
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}))
    type = filters.CharFilter(field_name='type__name', widget=forms.HiddenInput)

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(user__email__icontains=value) | Q(user__first_name__icontains=value) |
                               Q(user__last_name__icontains=value))

    class Meta:
        model = Application
        fields = ['search', 'status', 'type', 'user__under_age', 'promotional_code']
        form = ApplicationTableFilterForm
