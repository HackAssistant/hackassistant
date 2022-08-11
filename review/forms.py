from django import forms
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from application.models import ApplicationLog


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    bootstrap_field_info = {'': {'fields': [{'name': 'name'}, {'name': 'application'},
                                            {'name': 'comment', 'space': 12}]}}

    name = forms.CharField(initial='Comment', widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('instance', None) is not None:
            self.fields.get('comment').label = ''

    class Meta:
        model = ApplicationLog
        fields = ('comment', 'application', 'name')
        labels = {
            'comment': _('Add new comment')
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 2}),
            'application': forms.HiddenInput()
        }
