from django.contrib import admin

from application import models


class ApplicationAdmin(admin.ModelAdmin):
    list_filter = ('type', 'edition')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.ApplicationTypeConfig)
admin.site.register(models.ApplicationLog)
admin.site.register(models.Edition)
