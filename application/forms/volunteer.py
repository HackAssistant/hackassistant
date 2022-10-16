from django import forms
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from application.forms.base import ApplicationForm, PREVIOUS_HACKS, HACK_DAYS, ENGLISH_LEVELS


class VolunteerForm(ApplicationForm):
    bootstrap_field_info = {
        '': {
            'fields': [
                {'name': 'university', 'space': 6}, {'name': 'degree', 'space': 6},
                {'name': 'country', 'space': 6}, {'name': 'origin', 'space': 6}]},
        _('Hackathons'): {
            'fields': [{'name': 'night_shifts', 'space': 4}, {'name': 'first_time_volunteering', 'space': 4},
                       {'name': 'which_hack', 'space': 4, 'visible': {'first_time_volunteering': True}},
                       {'name': 'attendance', 'space': 4}, {'name': 'english_level', 'space': 4},
                       {'name': 'lennyface', 'space': 4}, {'name': 'friends', 'space': 6},
                       {'name': 'more_information', 'space': 6}, {'name': 'description', 'space': 6},
                       {'name': 'discover_hack', 'space': 6}],
            'description': _('Tell us a bit about your experience and preferences in this type of event.')},

    }

    university = forms.CharField(max_length=300, label=_('What university do you study at?'),
                                 help_text=_('Current or most recent school you attended.'))

    degree = forms.CharField(max_length=300, label=_('What\'s your major/degree?'),
                             help_text=_('Current or most recent degree you\'ve received'))

    first_time_volunteering = forms.TypedChoiceField(
        required=True,
        label=_('Have you volunteered in %s before?') % getattr(settings, 'HACKATHON_NAME'),
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, _('No')), (True, _('Yes'))),
        widget=forms.RadioSelect
    )

    which_hack = forms.MultipleChoiceField(
        required=False,
        label=_('Which %s editions have you volunteered in') % getattr(settings, 'HACKATHON_NAME'),
        widget=forms.CheckboxSelectMultiple,
        choices=PREVIOUS_HACKS
    )

    night_shifts = forms.TypedChoiceField(
        required=True,
        label=_('Would you be ok doing night shifts?'),
        help_text=_('Volunteering during 2am - 5am'),
        coerce=lambda x: x == 'True',
        choices=((False, _('No')), (True, _('Yes'))),
        widget=forms.RadioSelect
    )

    origin = forms.CharField(max_length=300, label=_('From which city?'))

    country = forms.CharField(max_length=300, label=_('From which country are you joining us?'))

    attendance = forms.MultipleChoiceField(
        required=True,
        label=_('Which days will you attend to %s?') % getattr(settings, 'HACKATHON_NAME'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'inline'}),
        choices=HACK_DAYS
    )

    english_level = forms.ChoiceField(
        required=True,
        label=_('How much confident are you talking in English?'),
        widget=forms.RadioSelect(attrs={'class': 'inline'}),
        choices=ENGLISH_LEVELS,
        help_text=_('1: I don\'t feel comfortable at all - 5: I\'m proficient '),
    )

    lennyface = forms.CharField(max_length=300, initial='-.-', label=_('Describe yourself in one "lenny face"?'),
                                help_text=mark_safe(
                                    _('tip: you can chose from here <a href="https://textsmili.es/" target="_blank"> '
                                      'https://textsmili.es/</a>')))

    friends = forms.CharField(
        required=False,
        label=_('If you\'re applying with friends, please mention their names.')
    )

    more_information = forms.CharField(
        required=False,
        label=_('There\'s something else we need to know?')
    )

    description = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3}),
                                  label=_('Why are you excited about %s?' % getattr(settings, 'HACKATHON_NAME')))

    discover_hack = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3}),
                                    label=_('How did you discover %s?' % getattr(settings, 'HACKATHON_NAME')))

    class Meta(ApplicationForm.Meta):
        description = _('Volunteers make the event possible by assisting the hackers and preparing the physical '
                        'spaces of the event. By joining our team of volunteers, you will get to know how this '
                        'amazing event works from the inside and meet amazing people and live a great experience!')
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json')},
            'degree': {'url': static('data/degrees.json')},
        }
