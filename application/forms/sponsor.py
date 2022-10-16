from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from application.forms.base import ApplicationForm, HACK_DAYS


class SponsorForm(ApplicationForm):
    bootstrap_field_info = {
        'Sponsor Info': {
            'fields': [{'name': 'company', 'space': 4}, {'name': 'position', 'space': 4},
                       {'name': 'attendance', 'space': 4}]}

    }

    full_name = forms.CharField(
        label=_('Full name')
    )

    phone_number = forms.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')], required=False,
                                   help_text=_("Phone number must be entered in the format: +#########'. "
                                               "Up to 15 digits allowed."),
                                   widget=forms.TextInput(attrs={'placeholder': '+#########'}))

    email = forms.EmailField(
        label=_('Email')
    )

    company = forms.CharField(
        label=_('Which company do you work for?')
    )

    position = forms.CharField(
        label=_('What is your job position?')
    )

    attendance = forms.MultipleChoiceField(
        required=True,
        label=_('Which days will you attend to %s?') % getattr(settings, 'HACKATHON_NAME'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
        choices=HACK_DAYS
    )
