import django_tables2 as tables
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

from application.models import ApplicationLog
from tables.mixins import AbstractTableMixin
from tables.utils import cache_tables


class VoteTable(AbstractTableMixin, tables.Table):
    counter = tables.TemplateColumn('{{ row_counter|add:1 }}', verbose_name='Position', orderable=False)

    @cache_tables
    def get_queryset(self):
        year_ago = timezone.now() - timezone.timedelta(days=365)
        votes = get_user_model().objects.filter(last_login__gt=year_ago, groups__name='Organizer')\
            .annotate(total_count=Count('vote'),
                      skip_count=Count('vote') - Count('vote__calculated_vote'),
                      vote_count=Count('vote__calculated_vote'))
        return list(votes)

    class Meta:
        model = get_user_model()
        attrs = {'class': 'table table-striped'}
        fields = ['counter', 'get_full_name', 'vote_count', 'skip_count', 'total_count']
        empty_text = 'No organizers voted yet... Why? :\'('
        order_by = '-total_count'


class ReactionTable(AbstractTableMixin, tables.Table):
    counter = tables.TemplateColumn('{{ row_counter|add:1 }}', verbose_name='Position', orderable=False)
    comment = tables.TemplateColumn(template_name='tables/comment_field_table.html')
    reaction_count = tables.Column(verbose_name='Reactions')

    @cache_tables
    def get_queryset(self):
        reactions = ApplicationLog.objects.exclude(comment='').annotate(reaction_count=Count('reactions__user'))\
            .exclude(reaction_count=0)
        return list(reactions)

    class Meta:
        model = ApplicationLog
        attrs = {'class': 'table table-striped'}
        fields = ['counter', 'comment', 'reaction_count']
        empty_text = 'No reactions... Why? :\'('
        order_by = '-reactions'
