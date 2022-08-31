import django_filters as filters
from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin


class CheckinTableFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'search', 'space': 12}]},
    }


class CheckinTableFilter(filters.FilterSet):
    search = filters.CharFilter(method='search_filter', label=_('Search'))

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(email__icontains=value) | Q(first_name__icontains=value) |
                               Q(last_name__icontains=value))

    class Meta:
        model = get_user_model()
        fields = ['search', ]
        form = CheckinTableFilterForm
