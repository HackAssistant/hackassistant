from django.forms import forms
import django_filters as filters

from app.mixins import BootstrapFormMixin
from application.models import Application
from django.utils.translation import gettext_lazy as _


class FriendsInviteTableFilterForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'half_accepted', 'space': 3}, {'name': 'are_pending', 'space': 3}]},
    }


class FriendsInviteTableFilter(filters.FilterSet):
    YES = 'yes'
    NO = 'no'
    CHOICES = ((YES, _('Yes')),
               (NO, _('No')))

    half_accepted = filters.ChoiceFilter(method='half_accepted_filter', choices=CHOICES,
                                         label=_('Are half members accepted?'))
    are_pending = filters.ChoiceFilter(method='pending_filter', choices=CHOICES,
                                       label=_('Is there any member on pending?'))

    def pending_filter(self, queryset, name, value):
        result = []
        operation = {self.YES: lambda x: x > 0, self.NO: lambda x: x <= 0}[value]
        for instance in queryset:
            if operation(instance['pending']):
                result.append(instance['code'])
        return queryset.filter(user__friendscode__code__in=result)

    def half_accepted_filter(self, queryset, name, value):
        result = []
        operation = {self.YES: lambda x, y: x <= y, self.NO: lambda x, y: x > y}[value]
        for instance in queryset:
            if operation((instance['members'] // 2), instance['accepted']):
                result.append(instance['code'])
        return queryset.filter(user__friendscode__code__in=result)

    class Meta:
        model = Application
        fields = ['half_accepted', 'are_pending']
        form = FriendsInviteTableFilterForm
