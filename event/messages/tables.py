import django_tables2 as tables

from event.messages.models import Announcement


class AnnouncementTable(tables.Table):
    actions = tables.TemplateColumn(template_name='tables/announcement_action.html', verbose_name='Actions',
                                    orderable=False)

    class Meta:
        model = Announcement
        attrs = {'class': 'table table-striped'}
        fields = ('name', 'sent', 'datetime', 'actions')
