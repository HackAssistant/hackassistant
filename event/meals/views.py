from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin
from django.shortcuts import render
from event.meals.tables import MealsTable
from event.meals.models import Meal

# TODO: create --> meal list 
#   First meal, closest to time
#   API amb python
# TODO: QR view (que el meal seleccionat no és actual)
# TODO: optional: meal edit i meal create (UI)


class MealsList(SingleTableMixin, TemplateView): # later on: AnyApplicationPermissionRequiredMixin / PermissionRequiredMixin
    # permission_required = 'event.meals.can_view_meals'
    template_name = 'meals_list.html'
    table_class = MealsTable

    def get_queryset(self):
        return Meal.objects.all()