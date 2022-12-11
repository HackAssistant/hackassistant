import django_filters as filters
from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from event.messages.models import Announcement


class AnnouncementFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'search', 'space': 12}]},
    }


class AnnouncementTableFilter(filters.FilterSet):
    search = filters.CharFilter(method='search_filter', label=_('Search'))

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(message__icontains=value))

    class Meta:
        model = Announcement
        fields = ['search', ]
        form = AnnouncementFilterForm
