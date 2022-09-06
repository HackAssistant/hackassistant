from django import forms
from django.contrib import admin

from application import models
from application.views import ApplicationApplyTemplate


class ApplicationAdmin(admin.ModelAdmin):
    list_filter = ('type', 'edition')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


class ApplicationTypeConfigAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.initial['file_review_fields'] = kwargs['instance'].get_file_review_fields()
            ApplicationForm = ApplicationApplyTemplate.get_form(kwargs['instance'].name)
            choices = []
            for name, field in ApplicationForm().declared_fields.items():
                if isinstance(field, forms.FileField):
                    choices.append((name, name))
            self.fields['file_review_fields'].widget = forms.CheckboxSelectMultiple(choices=choices)

    class Meta:
        model = models.ApplicationTypeConfig
        fields = '__all__'


class ApplicationTypeConfigAdmin(admin.ModelAdmin):
    form = ApplicationTypeConfigAdminForm


admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.ApplicationTypeConfig, ApplicationTypeConfigAdmin)
admin.site.register(models.ApplicationLog)
admin.site.register(models.Edition)
