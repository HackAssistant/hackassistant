from datetime import datetime

from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from application.models import Application
from application.validators import validate_file_extension

YEARS = [(year, str(year)) for year in range(datetime.now().year - 1, datetime.now().year + 6)]
DEFAULT_YEAR = datetime.now().year + 1
EXTENSIONS = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)

HACK_NAME = getattr(settings, 'HACKATHON_NAME')
EXTRA_NAME = [' 2016 Fall', ' 2016 Winter', ' 2017 Fall', '  2017 Winter', ' 2018', ' 2019', ' 2021', ' 2022']
PREVIOUS_HACKS = [(i, HACK_NAME + EXTRA_NAME[i]) for i in range(0, len(EXTRA_NAME))]
HACK_DAYS = [(x, x) for x in ['Friday', 'Saturday', 'Sunday']]
ENGLISH_LEVELS = [(x, x) for x in ['1', '2', '3', '4', '5']]


class ApplicationForm(BootstrapFormMixin, forms.ModelForm):

    diet_notice = forms.BooleanField(
        label=_('I authorize %s to use my food allergies and intolerances information to '
                'manage the catering service only.') % getattr(settings, 'HACKATHON_ORG')
    )

    exclude_save = ['terms_and_conditions', 'diet_notice']

    def save(self, commit=True):
        model_fields = [field.name for field in self.Meta.model._meta.fields]
        extra_fields = [field for field in self.declared_fields if field not in model_fields and
                        field not in self.exclude_save]
        files_fields = getattr(self, 'files', {})
        extra_data = {field: data for field, data in self.cleaned_data.items()
                      if field in extra_fields and field not in files_fields.keys()}
        self.instance.form_data = extra_data
        instance = super().save(commit)
        if commit:
            self.save_files(instance=instance)
        return instance

    def save_files(self, instance):
        files_fields = getattr(self, 'files', {})
        fs = FileSystemStorage()
        for field_name, file in files_fields.items():
            file_path = '%s/%s/%s_%s.%s' % (instance.type.name, field_name, instance.get_full_name().replace(' ', '-'),
                                            instance.get_uuid, file.name.split('.')[-1])
            if fs.exists(file_path):
                fs.delete(file_path)
            fs.save(name=file_path, content=file)
            form_data = instance.form_data
            form_data[field_name] = {'type': 'file', 'path': file_path}
            instance.form_data = form_data
        if len(files_fields) > 0:
            instance.save()
        return files_fields.keys()

    def get_hidden_edit_fields(self):
        return self.exclude_save

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.update(self.instance.form_data)
        instance = kwargs.get('instance', None)
        hidden_fields = self.get_hidden_edit_fields()
        if instance is not None and instance._state.db is not None:  # instance in DB
            for hidden_field in hidden_fields:
                self.fields.get(hidden_field).required = False

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        instance = getattr(self, 'instance', None)
        if instance is None or instance._state.db is None:  # instance not in DB
            policy_fields = self.get_policy_fields()
            fields.update({
                _('HackUPC Polices'): {
                    'fields': policy_fields,
                    'description': '<p style="color: margin-top: 1em;display: block;'
                                   'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                                   'process your information to organize an awesome hackathon. It '
                                   'will also include images and videos of yourself during the event. '
                                   'Your data will be used for admissions mainly.'
                                   'For more information on the processing of your '
                                   'personal data and on how to exercise your rights of access, '
                                   'rectification, suppression, limitation, portability and opposition '
                                   'please visit our Privacy and Cookies Policy.</p>'
                }})
        return fields

    def get_policy_fields(self):
        return [{'name': 'terms_and_conditions', 'space': 12}, {'name': 'diet_notice', 'space': 12}]

    class Meta:
        model = Application
        exclude = ['user', 'uuid', 'data', 'submission_date', 'status_update_date', 'status', 'contacted_by', 'type',
                   'last_modified', 'edition']
        help_texts = {
            'gender': _('This is for demographic purposes. You can skip this question if you want.'),
            'other_diet': _('Please fill here in your dietary requirements. '
                            'We want to make sure we have food for you!'),
            'origin': "Please select one of the dropdown options or write 'Others'. If the dropdown doesn't show up,"
                      " type following this schema: <strong>city, nation, country</strong>"
        }
        labels = {
            'gender': _('What gender do you identify as?'),
            'other_gender': _('Self-describe'),
            'tshirt_size': _('What\'s your t-shirt size?'),
            'diet': _('Dietary requirements'),
        }
    terms_and_conditions = forms.BooleanField(
        label=mark_safe(_('I\'ve read, understand and accept <a href="/terms_and_conditions" target="_blank">%s '
                          'Terms & Conditions</a> and <a href="/privacy_and_cookies" target="_blank">%s '
                          'Privacy and Cookies Policy</a>.' % (
                              getattr(settings, 'HACKATHON_NAME', ''), getattr(settings, 'HACKATHON_NAME', '')
                          )))
    )


# This class is linked to the instance of ApplicationTypeConfig where name = 'Hacker'
class HackerForm(ApplicationForm):
    bootstrap_field_info = {
        '': {
            'fields': [{'name': 'university', 'space': 4}, {'name': 'degree', 'space': 4},
                       {'name': 'lennyface', 'space': 4}, {'name': 'graduation_year', 'space': 8}]},
        _('Hackathons'): {
            'fields': [{'name': 'description', 'space': 6}, {'name': 'projects', 'space': 6},
                       {'name': 'first_timer', 'space': 12}, ]},
        _("Show us what you've built"): {
            'fields': [{'name': 'github', 'space': 6}, {'name': 'devpost', 'space': 6},
                       {'name': 'linkedin', 'space': 6}, {'name': 'site', 'space': 6},
                       {'name': 'resume', 'space': 12}, ],
            'description': 'Some of our sponsors may use this information for recruitment purposes, '
                           'so please include as much as you can.'},
        _('Traveling'): {
            'fields': [{'name': 'country', 'space': 6}, {'name': 'origin', 'space': 6}], }
    }

    phone_number = forms.CharField(validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')], required=False,
                                   help_text=_("Phone number must be entered in the format: +#########'. "
                                               "Up to 15 digits allowed."),
                                   widget=forms.TextInput(attrs={'placeholder': '+#########'}))

    origin = forms.CharField(max_length=300, label=_('From which city?'))

    country = forms.CharField(max_length=300, label=_('From which country are you joining us?'))

    # Is this your first hackathon?
    first_timer = forms.TypedChoiceField(
        required=True,
        label=_('Will %s be your first hackathon?' % getattr(settings, 'HACKATHON_NAME')),
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, _('No')), (True, _('Yes'))),
        widget=forms.RadioSelect
    )

    # Random lenny face
    lennyface = forms.CharField(max_length=300, initial='-.-', label=_('Describe yourself in one "lenny face"?'),
                                help_text=mark_safe(
                                    _('tip: you can chose from here <a href="https://textsmili.es/" target="_blank"> '
                                      'https://textsmili.es/</a>')))

    # University
    graduation_year = forms.IntegerField(initial=DEFAULT_YEAR,
                                         widget=forms.RadioSelect(choices=YEARS, attrs={'class': 'inline'}),
                                         label=_('What year will you graduate?'))
    university = forms.CharField(max_length=300, label=_('What university do you study at?'),
                                 help_text=_('Current or most recent school you attended.'))
    degree = forms.CharField(max_length=300, label=_('What\'s your major/degree?'),
                             help_text=_('Current or most recent degree you\'ve received'))

    # URLs
    github = forms.URLField(required=False,
                            widget=forms.TextInput(attrs={'placeholder': 'https://github.com/johnBiene'}))
    devpost = forms.URLField(required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'https://devpost.com/JohnBiene'}))
    linkedin = forms.URLField(required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'https://www.linkedin.com/in/john_biene'}))
    site = forms.URLField(required=False, widget=forms.TextInput(attrs={'placeholder': 'https://biene.space'}))

    # Explain a little bit what projects have you done lately
    projects = forms.CharField(required=False, max_length=500, widget=forms.Textarea(attrs={'rows': 3}), help_text=_(
        'You can talk about about past hackathons, personal projects, awards etc. (we love links) '
        'Show us your passion! :D'), label=_('What projects have you worked on?'))

    # Why do you want to come to X?
    description = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'rows': 3}),
                                  label=_('Why are you excited about %s?' % getattr(settings, 'HACKATHON_NAME')))

    # CV info
    resume_share = forms.BooleanField(required=False, initial=False, label=_(
        'I authorize %s to share my CV with %s Sponsors.' % (getattr(settings, 'HACKATHON_ORG'),
                                                             getattr(settings, 'HACKATHON_NAME'))))
    resume = forms.FileField(validators=[validate_file_extension], label=_('Upload your resume'), help_text=_(
        'Accepted file formats: %s' % (', '.join(EXTENSIONS) if EXTENSIONS else 'Any')))

    def get_policy_fields(self):
        policy_fields = super().get_policy_fields()
        policy_fields.extend([{'name': 'resume_share', 'space': 12}])
        return policy_fields

    def get_hidden_edit_fields(self):
        hidden_fields = super().get_hidden_edit_fields()
        hidden_fields.extend(['resume_share'])
        return hidden_fields

    class Meta(ApplicationForm.Meta):
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json')},
            'degree': {'url': static('data/degrees.json')},
        }
        icon_link = {
            'resume': 'bi bi-file-pdf-fill',
            'github': 'bi bi-github',
            'devpost': 'bi bi-collection-fill',
            'linkedin': 'bi bi-linkedin',
            'site': 'bi bi-globe',
        }


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
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json')},
            'degree': {'url': static('data/degrees.json')},
        }


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


class MentorForm(ApplicationForm):
    bootstrap_field_info = {
        '': {'fields': [
            {'name': 'university', 'space': 6}, {'name': 'degree', 'space': 6},
            {'name': 'country', 'space': 6}, {'name': 'origin', 'space': 6}, {'name': 'study_work', 'space': 6},
            {'name': 'company', 'space': 6, 'visible': {'study_work': 'True'}}]},
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

    class Meta(ApplicationForm.Meta):
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json')},
            'degree': {'url': static('data/degrees.json')},
        }
