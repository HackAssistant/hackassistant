import django_tables2 as tables

from application.models import Application


class ApplicationTable(tables.Table):
    full_name = tables.Column(accessor='user.get_full_name', order_by=('user.first_name', 'user.last_name'))
    detail = tables.TemplateColumn(template_name='tables/application_detail.html', verbose_name='Actions',
                                   orderable=False)
    last_modified = tables.TemplateColumn(template_code='{{ record.last_modified|timesince }}',
                                          order_by='last_modified')
    votes = tables.Column(accessor='vote_set.count', verbose_name='Votes', orderable=False)

    class Meta:
        model = Application
        attrs = {'class': 'table table-striped'}
        fields = ('full_name', 'user.email', 'status', 'votes', 'last_modified', 'detail')
        empty_text = 'No applications available'
