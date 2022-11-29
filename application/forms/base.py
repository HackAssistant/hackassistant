from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from app.utils import is_instance_on_db
from application.models import Application


YEARS = [(year, str(year)) for year in range(timezone.now().year - 1, timezone.now().year + 6)]
DEFAULT_YEAR = timezone.now().year + 1
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

    terms_and_conditions = forms.BooleanField(
        label=mark_safe(_('I\'ve read, understand and accept <a href="/terms_and_conditions" target="_blank">%s '
                          'Terms & Conditions</a> and <a href="/privacy_and_cookies" target="_blank">%s '
                          'Privacy and Cookies Policy</a>.' % (
                              getattr(settings, 'HACKATHON_NAME', ''), getattr(settings, 'HACKATHON_NAME', '')
                          )))
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
            file_path = '%s/%s/%s/%s_%s.%s' % (instance.edition.name, instance.type.name, field_name,
                                               instance.get_full_name().replace(' ', '-'), instance.get_uuid,
                                               file.name.split('.')[-1])
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
        return self.exclude_save.copy()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial.update(self.instance.form_data)
        instance = kwargs.get('instance', None)
        hidden_fields = self.get_hidden_edit_fields()
        if is_instance_on_db(instance):  # instance in DB
            for hidden_field in hidden_fields:
                self.fields.get(hidden_field).required = False

    def get_bootstrap_field_info(self):
        fields = super().get_bootstrap_field_info()
        instance = getattr(self, 'instance', None)
        if not is_instance_on_db(instance):  # instance not in DB
            policy_fields = self.get_policy_fields()
            fields.update({
                _('HackUPC Polices'): {
                    'fields': policy_fields,
                    'description': '<p style="color: margin-top: 1em;display: block;'
                                   'margin-bottom: 1em;line-height: 1.25em;">We, %s, '
                                   'process your information to organize an awesome hackathon. It '
                                   'will also include images and videos of yourself during the event. '
                                   'Your data will be used for admissions mainly. '
                                   'For more information on the processing of your '
                                   'personal data and on how to exercise your rights of access, '
                                   'rectification, suppression, limitation, portability and opposition '
                                   'please visit our Privacy and Cookies Policy.</p>' %
                                   getattr(settings, 'HACKATHON_ORG')
                }})
        fields[next(iter(fields))]['fields'].append({'name': 'promotional_code'})
        return fields

    def get_policy_fields(self):
        return [{'name': 'terms_and_conditions', 'space': 12}, {'name': 'diet_notice', 'space': 12}]

    def clean_promotional_code(self):
        promotional_code = self.cleaned_data.get('promotional_code', None)
        if promotional_code is not None:
            if promotional_code.usages != -1 and promotional_code.application_set.count() >= promotional_code.usages:
                raise ValidationError('This code is out of usages or not for this type')
        return promotional_code

    class Meta:
        model = Application
        description = ''
        exclude = ['user', 'uuid', 'data', 'submission_date', 'status_update_date', 'status', 'contacted_by', 'type',
                   'last_modified', 'edition']
        help_texts = {
            'gender': _('This is for demographic purposes. You can skip this question if you want.'),
            'other_diet': _('Please fill here in your dietary requirements. '
                            'We want to make sure we have food for you!'),
        }
        labels = {
            'gender': _('What gender do you identify as?'),
            'other_gender': _('Self-describe'),
            'tshirt_size': _('What\'s your t-shirt size?'),
            'diet': _('Dietary requirements'),
        }
        widgets = {
            'promotional_code': forms.HiddenInput
        }
