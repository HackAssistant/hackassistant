import django_tables2 as tables
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
