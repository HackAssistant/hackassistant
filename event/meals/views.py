from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin
from event.meals.tables import MealsTable
from event.meals.models import Meal, Eaten
from django.http import JsonResponse

from user.models import User


# TODO: create --> meal list
#   First meal, closest to time
#   API amb python
# TODO: QR view (que el meal seleccionat no és actual)
# TODO: optional: meal edit i meal create (UI)


class MealsList(SingleTableMixin,
                TemplateView):  # later on: AnyApplicationPermissionRequiredMixin / PermissionRequiredMixin
    # permission_required = 'event.meals.can_view_meals'
    template_name = 'meals_list.html'
    table_class = MealsTable

    def get_queryset(self):
        return Meal.objects.all()


# class CheckinList(AnyApplicationPermissionRequiredMixin, SingleTableMixin, FilterView):
#     permission_required = 'event.can_checkin'
#     template_name = 'checkin_list.html'
#     table_class = CheckinTable
#     filterset_class = CheckinTableFilter
#
#     def get_queryset(self):
#         return get_user_model().objects.filter(application__status=Application.STATUS_CONFIRMED,
#                                                application__edition=Edition.get_default_edition()).distinct()
class CheckinMeal(TemplateView):
    template_name = 'checkin_meal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            mid = kwargs.get('mid')
            meal = Meal.objects.get(id=mid)
            context.update({'meal': meal})
        except (Meal.DoesNotExist, ValueError):
            return {'meal_obj': ''}
        return context

    # def has_permission(self, types):
    #     permission = 'event.meals.can_checkin'
    #     if self.request.user.has_perm(permission):
    #         return True
    #     for application_type in types:
    #         if not self.request.user.has_perm('%s_%s' % (permission, application_type.lower())):
    #             return False
    #     return True

    def post(self, request, *args, **kwargs):
        # DB retrieve
        meal_id = kwargs.get('mid')
        try:
            meal = Meal.objects.get(id=meal_id)
        except (Meal.DoesNotExist, ValueError):
            return JsonResponse({'message': 'Meal not found with id: ' + meal_id + ". Please try again"}, status=404)
        try:
            user = User.objects.get(qr_code=request.POST.get("qrCode"))
        except (User.DoesNotExist, ValueError):
            return JsonResponse({'message': 'User not found with QRCode: ' + request.POST.get(
                "qrCode") + ". Please try again"}, status=404)
        uid = user.id
        entries = Eaten.objects.all().filter(user_id=uid, meal_id=meal_id)
        n_times_eaten = entries.count()
        times_str = str(n_times_eaten) + "/" + str(meal.times)
        if n_times_eaten < meal.times:
            # Create a new entry
            eaten = Eaten(user_id=uid, meal_id=meal_id)
            eaten.save()
            diet = user.get_diet_display()
            other_diet = user.other_diet
            return JsonResponse({'success': True, 'message': 'User allowed to eat', 'diet': diet, 'other_diet': other_diet, 'times': times_str})

        if n_times_eaten >= meal.times:
            # user has eaten the limited quantity.
            times_str = str(n_times_eaten) + "/" + str(meal.times)
            return JsonResponse({'success': False, 'message': 'User has already eaten', 'times': times_str,
                                 'timeSinceLastEaten': [i.time.timestamp() for i in entries.order_by('-time')][0]})
