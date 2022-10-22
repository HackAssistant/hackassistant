import django_filters as filters
from django import forms
from django.utils.translation import gettext as _

from app.mixins import BootstrapFormMixin
from application.models import ApplicationTypeConfig, Application, Edition
from stats.base import StatsFilterMixin
from user.models import User


class UserStatsFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'applied_as', 'space': 12}, {'name': 'status', 'space': 12},
                   {'name': 'gender', 'space': 12}, {'name': 'under_age', 'space': 12}]},
    }


class UserStatsFilter(StatsFilterMixin, filters.FilterSet):
    applied_as = filters.ModelMultipleChoiceFilter(label=_('Applied as'),
                                                   widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
                                                   queryset=ApplicationTypeConfig.objects.all(),
                                                   method='applied_as_filter')
    status = filters.MultipleChoiceFilter(label=_('Application status'),
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
                                          choices=Application.STATUS, method='status_filter')
    gender = filters.MultipleChoiceFilter(label=_('Gender'), choices=User.GENDERS,
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}))
    under_age = filters.TypedChoiceFilter(label=_('Age'), coerce=lambda x: x == 'True',
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
                                          choices=((False, '18 or over'), (True, 'Between 14 (included) and 18')), )

    def applied_as_filter(self, queryset, name, value):
        edition = Edition.get_default_edition()
        return queryset.filter(application_set__type__in=value, application_set__edition=edition).distict()

    def status_filter(self, queryset, name, value):
        edition = Edition.get_default_edition()
        return queryset.filter(application_set__status__in=value, application_set__edition=edition).distict()

    def filter_applied_as(self, instance, value):
        edition = Edition.get_default_edition()
        return instance.application_set.filter(type__in=value, edition=edition).exists()

    def filter_status(self, instance, value):
        edition = Edition.get_default_edition()
        return instance.application_set.filter(status__in=value, edition=edition).exists()

    def filter_gender(self, instance, value):
        return instance.gender == value

    def filter_under_age(self, instance, value):
        return instance.under_age == value

    class Meta:
        model = User
        form = UserStatsFilterForm
        fields = ['applied_as', 'status', 'gender', 'under_age']
