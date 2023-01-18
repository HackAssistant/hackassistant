from django import forms
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from event.messages.models import Announcement
from event.messages.services import MessageServiceManager


class AnnouncementModelFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(x, x.replace('MessageService', '')) for x in MessageServiceManager.get_services_names()]
        self.fields['services'].widget = forms.CheckboxSelectMultiple(choices=choices)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            self.initial['services'] = kwargs['instance'].get_services()


class AnnouncementForm(BootstrapFormMixin, AnnouncementModelFormMixin, forms.ModelForm):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'name', 'space': 12}, {'name': 'datetime', 'space': 4}, {'name': 'status', 'space': 4},
                   {'name': 'services', 'space': 4}, {'name': 'message', 'space': 12}]
    }}

    class Meta:
        model = Announcement
        exclude = ('id', )
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4})
        }
        labels = {
            'sent': _('Message sent')
        }
        help_texts = {
            'sent': _('The message will be sent immediately if you modify this field to sent status!')
        }
