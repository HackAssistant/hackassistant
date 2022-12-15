import django_tables2 as tables
from django.contrib.auth import get_user_model

from event.meals.models import Meal


class MealsTable(tables.Table):
    starts = tables.DateTimeColumn(format='d/m/Y, H:i:s')
    ends = tables.DateTimeColumn(format='d/m/Y, H:i:s')
    actions = tables.TemplateColumn(template_name='tables/meals_action.html', verbose_name='Actions', orderable=False)

    class Meta:
        # model's name
        model = Meal
        # HTML classes
        attrs = {'class': 'table table-striped'}
        # Table columns
        fields = ('name', 'starts', 'ends', 'times', 'actions')  # opt: kind
        order_by = ('starts', )


class CheckinMealTable(tables.Table):
    full_name = tables.Column(accessor='get_full_name', order_by=('first_name', 'last_name'))
    actions = tables.TemplateColumn(template_name='tables/checkin_meal_action.html', verbose_name='Actions',
                                    orderable=False)

    class Meta:
        model = get_user_model()
        attrs = {'class': 'table table-striped'}
        fields = ('full_name', 'actions')
