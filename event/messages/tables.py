import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from event.messages.models import Announcement


class AnnouncementTable(tables.Table):
    status = tables.TemplateColumn(template_name='tables/status.html', verbose_name=_('Status'))
    actions = tables.TemplateColumn(template_name='tables/announcement_action.html', verbose_name=_('Actions'),
                                    orderable=False)

    class Meta:
        model = Announcement
        attrs = {'class': 'table table-striped'}
        fields = ('name', 'status', 'datetime', 'actions')
