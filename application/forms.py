from datetime import datetime

from django import forms
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.forms.utils import ErrorList
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from application.models import Application
from application.validators import validate_file_extension


class ApplicationForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.update(self.instance.form_data)

    class Meta:
        model = Application
        exclude = ['user', 'uuid', 'data', 'submission_date', 'status_update_date', 'status', 'contacted_by', 'type']
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


# This class is linked to the instance of ApplicationTypeConfig where name = 'Hacker'
class HackerForm(BootstrapFormMixin, ApplicationForm):
    YEARS = [(year, str(year)) for year in range(datetime.now().year - 1, datetime.now().year + 6)]
    DEFAULT_YEAR = datetime.now().year + 1
    EXTENSIONS = getattr(settings, 'SUPPORTED_RESUME_EXTENSIONS', None)

    bootstrap_field_info = {_('Personal Info'): {'fields': [
        {'name': 'university', 'space': 4}, {'name': 'degree', 'space': 4}, {'name': 'phone_number', 'space': 4},
        {'name': 'tshirt_size', 'space': 4}, {'name': 'diet', 'space': 4},
        {'name': 'other_diet', 'space': 4, 'visible': {'diet': Application.DIET_OTHER}},
        {'name': 'under_age', 'space': 4}, {'name': 'gender', 'space': 4},
        {'name': 'other_gender', 'space': 4, 'visible': {'gender': Application.GENDER_OTHER}},
        {'name': 'graduation_year', 'space': 8},
        {'name': 'lennyface', 'space': 4}],
        'description': _('Hey there, before we begin we would like to know a little more about you.')},
        'Hackathons?': {
            'fields': [{'name': 'description', 'space': 6}, {'name': 'projects', 'space': 6},
                       {'name': 'first_timer', 'space': 12}, ]
        },
        'Show us what you\'ve built': {
            'fields': [{'name': 'github', 'space': 6}, {'name': 'devpost', 'space': 6},
                       {'name': 'linkedin', 'space': 6}, {'name': 'site', 'space': 6},
                       {'name': 'resume', 'space': 12}, ],
            'description': 'Some of our sponsors may use this information for recruitment purposes, '
                           'so please include as much as you can.'
        },
        'Traveling': {
            'fields': [{'name': 'country', 'space': 6}, {'name': 'origin', 'space': 6}],
        }
    }

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        instance = getattr(self, 'instance', None)
        if instance is not None and instance._state.adding:  # instance not in DB
            fields.update({
                'HackUPC Polices': {
                    'fields': [{'name': 'terms_and_conditions', 'space': 12}, {'name': 'diet_notice', 'space': 12},
                               {'name': 'resume_share', 'space': 12}],
                    'description': '<p style="color: margin-top: 1em;display: block;'
                                   'margin-bottom: 1em;line-height: 1.25em;">We, Hackers at UPC, '
                                   'process your information to organize an awesome hackaton. It '
                                   'will also include images and videos of yourself during the event. '
                                   'Your data will be used for admissions mainly. We may also reach '
                                   'out to you (sending you an e-mail) about other events that we are '
                                   'organizing and that are of a similar nature to those previously '
                                   'requested by you. For more information on the processing of your '
                                   'personal data and on how to exercise your rights of access, '
                                   'rectification, suppression, limitation, portability and opposition '
                                   'please visit our Privacy and Cookies Policy.</p>'
                }})
        return fields

    exclude_save = ['terms_and_conditions', 'diet_notice']

    under_age = forms.TypedChoiceField(
        required=True,
        label=_('How old are you?'),
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, _('18 or over')), (True, _('Between 14 (included) and 18'))),
        widget=forms.RadioSelect
    )

    terms_and_conditions = forms.BooleanField(
        label=mark_safe(_('I\'ve read, understand and accept <a href="/terms_and_conditions" target="_blank">%s '
                          'Terms & Conditions</a> and <a href="/privacy_and_cookies" target="_blank">%s '
                          'Privacy and Cookies Policy</a>.' % (
                              getattr(settings, 'HACKATHON_NAME', ''), getattr(settings, 'HACKATHON_NAME', '')
                          )))
    )

    diet_notice = forms.BooleanField(
        label=_('I authorize "Hackers at UPC" to use my food allergies and intolerances information to '
                'manage the catering service only.')
    )

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
                                    _('tip: you can chose from here <a href="http://textsmili.es/" target="_blank"> http://textsmili.es/</a>')))

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

    class Meta(ApplicationForm.Meta):
        api_fields = {
            'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
            'university': {'url': static('data/universities.json')},
            'degree': {'url': static('data/degrees.json')},
        }
