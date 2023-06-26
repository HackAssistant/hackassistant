import django_filters as filters
from django import forms
from django.contrib.auth import get_user_model

from app.mixins import BootstrapFormMixin
from tables.mixins import TablesFiltersMixin


#  Filter methods must return True/False if item must be on list or not
#  def filter_field_name(self, instance, form_value)


class VoteTableFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'get_full_name', 'space': 12}]},
    }


class VoteTableFilter(TablesFiltersMixin, filters.FilterSet):
    get_full_name = filters.CharFilter(label='Name')

    def filter_get_full_name(self, instance, form_value):
        return form_value in instance.get_full_name()

    class Meta:
        model = get_user_model()
        fields = ('get_full_name', )
        form = VoteTableFilterForm
