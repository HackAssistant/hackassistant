import django_tables2 as tables
from django.db.models import F, Avg, Count, Q

from app.tables import FloatColumn
from application.models import Application


class FriendInviteTable(tables.Table):
    select = tables.CheckBoxColumn(accessor='code', attrs={"th__input": {"onclick": "select_all(this)",
                                                                         'class': 'form-check-input'},
                                                           'td__input': {'class': 'form-check-input'}})
    vote_avg = FloatColumn(float_digits=3)
    pending = tables.Column(attrs={'td': {'class': 'pending'}})

    @staticmethod
    def get_queryset(queryset):
        return queryset.values('user__friendscode__code').annotate(
            code=F('user__friendscode__code'),
            vote_avg=Avg('vote__calculated_vote'),
            members=Count('user'),
            pending=Count('user', filter=Q(status=Application.STATUS_PENDING)),
            invited=Count('user', filter=Q(status=Application.STATUS_INVITED)),
            accepted=Count('user', filter=Q(status=Application.STATUS_CONFIRMED)))

    class Meta:
        model = Application
        attrs = {'class': 'table table-striped'}
        fields = ('select', 'code', 'vote_avg', 'members', 'pending', 'invited', 'accepted')
        empty_text = 'No friends :\'('
        order_by = 'vote_avg'
