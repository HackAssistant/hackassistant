import django_tables2 as tables
from django.db.models import Avg, F, Count

from application.models import Application


class ApplicationTable(tables.Table):
    full_name = tables.Column(accessor='user.get_full_name', order_by=('user.first_name', 'user.last_name'))
    detail = tables.TemplateColumn(template_name='tables/application_detail.html', verbose_name='Actions',
                                   orderable=False)
    last_modified = tables.TemplateColumn(template_code='{{ record.last_modified|timesince }}',
                                          order_by='last_modified')
    votes = tables.Column(accessor='vote_count', verbose_name='Votes')

    status = tables.TemplateColumn(template_name='tables/status.html')

    @staticmethod
    def get_queryset(queryset):
        return queryset.annotate(vote_avg=Avg('vote__calculated_vote'), vote_count=Count('vote'))

    def order_vote_avg(self, queryset, is_descending):
        queryset = queryset.order_by(F('vote_avg').desc(nulls_last=True) if is_descending else 'vote_avg')
        return queryset, True

    class Meta:
        model = Application
        attrs = {'class': 'table table-striped'}
        fields = ('full_name', 'user.email', 'status', 'votes', 'vote_avg', 'last_modified', 'detail')
        empty_text = 'No applications available'
        order_by = 'vote_avg'


class ApplicationTableWithPromotion(ApplicationTable):
    promotional_code = tables.TemplateColumn(template_name='tables/promotional_code.html')

    class Meta(ApplicationTable.Meta):
        fields = ('full_name', 'user.email', 'status', 'promotional_code', 'votes', 'vote_avg', 'last_modified',
                  'detail')


class ApplicationInviteTable(ApplicationTable):
    select = tables.CheckBoxColumn(accessor='pk', attrs={"th__input": {"onclick": "select_all(this)",
                                                                       'class': 'form-check-input'},
                                                         'td__input': {'class': 'form-check-input'}})

    class Meta(ApplicationTable.Meta):
        fields = ('select', 'full_name', 'user.email', 'status', 'votes', 'vote_avg', 'last_modified', 'detail')
