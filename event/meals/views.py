from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin
from django.shortcuts import render
from event.meals.tables import MealsTable
from event.meals.models import Meal
from django.http import Http404

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

class CheckinMeal(TemplateView):
    template_name = 'checkin_meal.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            mid = kwargs.get('mid')
            result = Meal.objects.get(id=mid)
            print(result)
            context.update({'meal_obj': result})
        except (Meal.DoesNotExist, ValueError):
            return {'meal_obj':''}
        return context

    # def has_permission(self, types):
    #     permission = 'event.meals.can_checkin'
    #     if self.request.user.has_perm(permission):
    #         return True
    #     for application_type in types:
    #         if not self.request.user.has_perm('%s_%s' % (permission, application_type.lower())):
    #             return False
    #     return True