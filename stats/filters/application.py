import django_filters as filters
from django import forms
from django.utils.translation import gettext as _

from app.mixins import BootstrapFormMixin
from application.models import ApplicationTypeConfig, Application, Edition
from stats.base import StatsFilterMixin
from user.models import User


class ApplicationStatsFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'type', 'space': 12}, {'name': 'status', 'space': 12}]},
    }


class ApplicationStatsFilter(StatsFilterMixin, filters.FilterSet):
    type = filters.ModelMultipleChoiceFilter(label=_('Type'),
                                             widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
                                             queryset=ApplicationTypeConfig.objects.all())
    status = filters.MultipleChoiceFilter(label=_('Application status'),
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
                                          choices=Application.STATUS)

    def filter_type(self, instance, value):
        return instance.type in value

    def filter_status(self, instance, value):
        return instance.status in value

    class Meta:
        model = Application
        form = ApplicationStatsFilterForm
        fields = ['type', 'status']
