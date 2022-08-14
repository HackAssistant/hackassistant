from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app.mixins import BootstrapFormMixin
from application.models import ApplicationLog, Application
from review.emails import send_dubious_email


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


class DubiousApplicationForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {_(''): {'fields': [{'name': 'reason', 'space': 12}]}}

    status = forms.ChoiceField(widget=forms.HiddenInput, choices=(
        (Application.STATUS_NEEDS_CHANGE, 'A'), (Application.STATUS_PENDING, 'B'), (Application.STATUS_INVALID, 'C')))
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}),
                             label=_('For what reason this application is/is not dubious'),
                             help_text=_('BE CAREFUL, this text will be sent to the hacker if you confirm or '
                                         'invalidate'))

    def save(self, application, request):
        new_status = self.cleaned_data.get('status')
        reason = self.cleaned_data.get('reason')
        url = reverse('change_status_application', kwargs={'uuid': application.get_uuid,
                                                           'status': new_status})
        query_params = {}
        if new_status == application.STATUS_PENDING:
            query_params.update({'comment': ('Not dubious: ' if application.status == application.STATUS_DUBIOUS
                                             else 'Corrected: ') + reason})
        elif new_status == application.STATUS_INVALID:
            query_params.update({'comment': 'Invalid: ' + reason})
            send_dubious_email(application=application, request=request, reason=reason, name='invalidate_dubious')
        elif new_status == application.STATUS_NEEDS_CHANGE:
            send_dubious_email(application=application, request=request, reason=reason, name='confirm_dubious')
        return url, query_params
