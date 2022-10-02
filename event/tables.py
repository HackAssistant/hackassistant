import django_tables2 as tables
from django.contrib.auth import get_user_model


class CheckinTable(tables.Table):
    full_name = tables.Column(accessor='get_full_name', order_by=('first_name', 'last_name'))
    actions = tables.TemplateColumn(template_name='tables/checkin_action.html', verbose_name='Actions', orderable=False)

    class Meta:
        model = get_user_model()
        attrs = {'class': 'table table-striped'}
        fields = ('full_name', 'email', 'actions')
