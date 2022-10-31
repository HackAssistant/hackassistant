from django import forms
from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from application.forms.base import ApplicationForm, DEFAULT_YEAR, YEARS, FIELD_OF_EXPERTISE


# This class is linked to the instance of ApplicationTypeConfig where name = 'Hacker'
class HackerForm(ApplicationForm):
    bootstrap_field_info = {
        '': {
            'fields': [{'name': 'country', 'space': 6}, {'name': 'origin', 'space': 6},
                       {'name': 'study_work', 'space': 4}, {'name': 'university', 'space': 4,
                                                            'visible': {'study_work': 'Study'}},
                       {'name': 'graduation_year', 'space': 4, 'visible': {'study_work': 'Study'}}]},
        _('Hackathons'): {
            'fields': [{'name': 'first_timer', 'space': 4}, {'name': 'field_of_expertise', 'space': 8}]},
    }

    country = forms.CharField(max_length=300, label=_('From which country are you joining us?'))

    origin = forms.CharField(max_length=300, label=_('From which city?'))

    # Is this your first hackathon?
    first_timer = forms.TypedChoiceField(
        required=True,
        label=_('Will %s be your first hackathon?' % getattr(settings, 'HACKATHON_NAME')),
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, _('No')), (True, _('Yes'))),
        widget=forms.RadioSelect
    )

    study_work = forms.TypedChoiceField(
        required=True,
        label='Are you studying or working?',
        choices=(('Study', _('Study')), ('Work', _('Work'))),
        widget=forms.RadioSelect(attrs={'class': 'inline'})
    )

    # University
    graduation_year = forms.IntegerField(required=False, initial=DEFAULT_YEAR,
                                         widget=forms.RadioSelect(choices=YEARS, attrs={'class': 'inline'}),
                                         label=_('What year will you graduate?'))
    university = forms.CharField(required=False, max_length=300, label=_('What university do you study at?'),
                                 help_text=_('Current or most recent school you attended.'))

    field_of_expertise = forms.TypedChoiceField(
        label=_('Which is your field of expertise?'),
        widget=forms.RadioSelect(attrs={'class': 'inline'}),
        choices=FIELD_OF_EXPERTISE
    )

    def get_policy_fields(self):
        policy_fields = super().get_policy_fields()
        return policy_fields

    def get_hidden_edit_fields(self):
        hidden_fields = super().get_hidden_edit_fields()
        return hidden_fields

    class Meta(ApplicationForm.Meta):
        description = _('You will join a team with which you will do a project in a weekend. '
                        'You will meet new people and learn a lot, don\'t think about it and apply!')
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json'), 'others': True},
            'degree': {'url': static('data/degrees.json')},
        }
