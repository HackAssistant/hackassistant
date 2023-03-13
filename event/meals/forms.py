from django import forms
from django.core.exceptions import ValidationError

from app.mixins import BootstrapFormMixin
from event.meals.models import Meal


class MealForm(BootstrapFormMixin, forms.ModelForm):
    bootstrap_field_info = {'': {
        'fields': [{'name': 'name', 'space': 6}, {'name': 'kind', 'space': 6}, {'name': 'starts', 'space': 4},
                   {'name': 'ends', 'space': 4}, {'name': 'times', 'space': 4}]
    }}

    def clean(self):
        starts = self.cleaned_data.get('starts', None)
        ends = self.cleaned_data.get('ends', None)
        if starts is None or ends is None or starts >= ends:
            self.add_error('starts', '')
            self.add_error('ends', '')
            raise ValidationError('Start time must be before ending time!')
        return self.cleaned_data

    class Meta:
        model = Meal
        exclude = ('id', )
