from django import forms
from django.contrib import admin

from event.messages.forms import AnnouncementModelFormMixin
from event.messages.models import Announcement


class AnnouncementAdminForm(AnnouncementModelFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'


class AnnouncementAdmin(admin.ModelAdmin):
    list_filter = ('sent', 'services')
    search_fields = ('name', 'message')
    form = AnnouncementAdminForm


admin.site.register(Announcement, AnnouncementAdmin)
