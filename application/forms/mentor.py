from django import forms
from django.conf import settings
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from application.forms.base import ApplicationForm, FIELD_OF_EXPERTISE


class MentorForm(ApplicationForm):
    bootstrap_field_info = {
        '': {'fields': [
            {'name': 'university', 'space': 6}, {'name': 'degree', 'space': 6},
            {'name': 'country', 'space': 6}, {'name': 'origin', 'space': 6}, {'name': 'field_of_expertise', 'space': 4},
            {'name': 'study_work', 'space': 4}, {'name': 'company', 'space': 4, 'visible': {'study_work': 'True'}}]},
        'Hackathons': {
            'fields': [{'name': 'first_timer', 'space': 4},
                       {'name': 'previous_roles', 'space': 4, 'visible': {'first_timer': 'False'}},
                       {'name': 'more_information', 'space': 12}],
            'description': _('Tell us a bit about your experience and preferences in this type of event.')},
    }

    university = forms.CharField(max_length=300, label=_('What university do you study at?'),
                                 help_text=_('Current or most recent school you attended.'))

    degree = forms.CharField(max_length=300, label=_('What\'s your major/degree?'),
                             help_text=_('Current or most recent degree you\'ve received'))

    origin = forms.CharField(max_length=300, label=_('From which city?'))

    country = forms.CharField(max_length=300, label=_('From which country are you joining us?'))

    study_work = forms.TypedChoiceField(
        required=True,
        label='Are you studying or working?',
        coerce=lambda x: x == 'True',
        choices=((False, _('Study')), (True, _('Work'))),
        widget=forms.RadioSelect(attrs={'class': 'inline'})
    )

    company = forms.CharField(required=False,
                              help_text='Current or most recent company you attended',
                              label='Where are you working at?')

    first_timer = forms.TypedChoiceField(
        required=True,
        label=_('Will %s be your first hackathon?' % getattr(settings, 'HACKATHON_NAME')),
        initial=True,
        coerce=lambda x: x == 'True',
        choices=((False, _('No')), (True, _('Yes'))),
        widget=forms.RadioSelect
    )

    previous_roles = forms.MultipleChoiceField(
        required=False,
        label=_('Did you participate as a hacker, mentor, or volunteer?'),
        widget=forms.CheckboxSelectMultiple,
        choices=(('Hacker', _('Hacker')), ('Mentor', _('Mentor')), ('Volunteer', _('Volunteer')))
    )

    more_information = forms.CharField(
        required=False,
        label=_('There\'s something else we need to know?')
    )

    field_of_expertise = forms.TypedChoiceField(
        label=_('Which is your field of expertise?'),
        widget=forms.RadioSelect(attrs={'class': 'inline'}),
        choices=FIELD_OF_EXPERTISE
    )

    class Meta(ApplicationForm.Meta):
        description = _('Help and motivate hackers with your knowledge. Either because you are passionate about it'
                        ', or if you\'ve graduated more than a year ago and can\'t participate as a hacker, '
                        'apply now as a mentor!')
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json')},
            'degree': {'url': static('data/degrees.json')},
        }
