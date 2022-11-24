from django import forms
from django.contrib import admin

from application import models


class ApplicationAdmin(admin.ModelAdmin):
    list_filter = ('type', 'edition')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


class ApplicationTypeConfigAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from application.views import ApplicationApply
        if 'instance' in kwargs:
            self.initial['file_review_fields'] = kwargs['instance'].get_file_review_fields()
            ApplicationForm = ApplicationApply.get_form_class(kwargs['instance'].name)
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
    exclude = ('name', )

    def has_add_permission(self, request, obj=None):
        return False


class PromotionalCodeAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', )


admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.ApplicationTypeConfig, ApplicationTypeConfigAdmin)
admin.site.register(models.ApplicationLog)
admin.site.register(models.Edition)
admin.site.register(models.PromotionalCode, PromotionalCodeAdmin)
