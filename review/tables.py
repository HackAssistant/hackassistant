import django_tables2 as tables
from django.db.models.functions import Lower

from application.models import Application


class ApplicationTable(tables.Table):
    full_name = tables.Column(accessor='user.get_full_name', order_by=('user.first_name', 'user.last_name'))
    detail = tables.TemplateColumn("<a href='{% url 'application_detail' record.uuid %}'>Detail</a> ",
                                   verbose_name='Actions', orderable=False)
    votes = tables.Column(accessor='vote_set.count', verbose_name='Votes', orderable=False)

    class Meta:
        model = Application
        attrs = {'class': 'table table-striped'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ('full_name', 'user.email', 'status', 'votes', 'detail')
        empty_text = 'No applications available'
