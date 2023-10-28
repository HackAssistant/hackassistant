import django_tables2 as tables
from django.db.models import Avg, F, Count

from app.tables import FloatColumn, TruncatedEmailColumn, TruncatedTextColumn
from application.models import Application


class ApplicationTable(tables.Table):
    full_name = TruncatedTextColumn(accessor='user.get_full_name', order_by=('user.first_name', 'user.last_name'))
    detail = tables.TemplateColumn(template_name='tables/application_detail.html', verbose_name='Actions',
                                   orderable=False)
    last_modified = tables.TemplateColumn(template_code='{{ record.last_modified|timesince }}',
                                          order_by='last_modified')
    votes = tables.Column(accessor='vote_count', verbose_name='Votes')
    status = tables.TemplateColumn(template_name='tables/status.html')
    vote_avg = FloatColumn(float_digits=3)
    email = TruncatedEmailColumn(accessor='user.email')
    promotional_code = tables.TemplateColumn(template_name='tables/promotional_code.html')
    slip = tables.TemplateColumn(template_name='tables/permission_slip.html', orderable=False)

    def __init__(self, promotional_code=False, slip=False, *args, **kwargs):
        self.base_columns['promotional_code'].visible = promotional_code
        self.base_columns['slip'].visible = slip
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_queryset(queryset):
        return queryset.annotate(vote_avg=Avg('vote__calculated_vote'), vote_count=Count('vote'))

    def order_vote_avg(self, queryset, is_descending):
        queryset = queryset.order_by(F('vote_avg').desc(nulls_last=True) if is_descending else 'vote_avg')
        return queryset, True

    class Meta:
        model = Application
        attrs = {'class': 'table table-striped'}
        fields = ('full_name', 'email', 'status', 'promotional_code', 'votes', 'vote_avg', 'slip', 'last_modified',
                  'detail')
        empty_text = 'No applications available'
        order_by = 'vote_avg'


class ApplicationInviteTable(ApplicationTable):
    select = tables.CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "select_all(this)",
                                                                       'class': 'form-check-input'},
                                                         'td__input': {'class': 'form-check-input'}})

    class Meta(ApplicationTable.Meta):
        fields = ('select', 'full_name', 'email', 'status', 'promotional_code', 'votes', 'vote_avg',
                  'last_modified', 'detail')
