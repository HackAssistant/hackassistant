from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin


class FriendsForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {'fields': [{'name': 'friends_code', 'space': 12}, ]}}

    friends_code = forms.CharField(label=_('Friends\' code'), max_length=getattr(settings, "FRIEND_CODE_LENGTH", 13),
                                   required=False)
