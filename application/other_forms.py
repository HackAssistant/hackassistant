import os

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from application.models import PermissionSlip
from application.validators import validate_file_extension

EXTENSIONS = getattr(settings, 'SUPPORTED_PERMISSION_SLIP_EXTENSIONS', None)


class PermissionSlipForm(forms.ModelForm, BootstrapFormMixin):
    bootstrap_field_info = {'': {'fields': [{'name': 'file', 'space': 12}, {'name': 'terms', 'space': 12}]}}

    file = forms.FileField(validators=[validate_file_extension(EXTENSIONS)], required=True,
                           label=_('Upload your permission slip'),
                           help_text=_('Accepted file formats: %s' % (', '.join(EXTENSIONS) if EXTENSIONS else 'Any')))
    terms = forms.BooleanField(label=_('I understand that the permission slip I am providing will be used for '
                                       'ensuring my safety during the event and for addressing any legal aspects '
                                       'related to my participation in the hackathon. I hereby consent to the '
                                       'use of this document for these purposes.'), required=True)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        self._old_file = instance.file if instance is not None else None
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.status = instance.STATUS_UPLOADED
        old_file = getattr(self, '_old_file', None)
        try:
            os.remove(old_file.path)
        except ValueError:
            pass
        if commit:
            instance.save()
        return instance

    class Meta:
        model = PermissionSlip
        fields = ('file', 'terms')
