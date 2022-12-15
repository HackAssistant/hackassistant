from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from application.models import Application, Edition
from event.meals.filters import MealsTableFilter
from event.meals.tables import MealsTable, CheckinMealTable
from event.meals.models import Meal, Eaten
from django.http import JsonResponse
from application.mixins import PermissionRequiredMixin

from user.models import User


# TODO: create --> meal list
#   First meal, closest to time
#   API amb python
# TODO: QR view (que el meal seleccionat no és actual)
# TODO: optional: meal edit i meal create (UI)


class MealsList(PermissionRequiredMixin, SingleTableMixin, TemplateView):
    permission_required = 'event.can_checkin_meals'
    template_name = 'meals_list.html'
    table_class = MealsTable

    def get_queryset(self):
        return Meal.objects.all()


class CheckinMeal(PermissionRequiredMixin, SingleTableMixin, FilterView):
    template_name = 'checkin_meal.html'
    permission_required = 'event.can_checkin_meals'
    table_class = CheckinMealTable
    filterset_class = MealsTableFilter

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return get_user_model().objects.filter(application__status=Application.STATUS_ATTENDED,
                                               application__edition=Edition.get_default_edition()).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meal = get_object_or_404(Meal, id=self.kwargs.get('mid'))
        context.update({'meal': meal})
        return context

    def post(self, request, *args, **kwargs):
        # DB retrieve
        meal = get_object_or_404(Meal, id=self.kwargs.get('mid'))
        try:
            qr_code = request.POST.get("qr_code")
            if qr_code is None:
                raise ValueError
        except ValueError:
            return JsonResponse({'errors': ['QR code is required.']}, status=400)
        try:
            user = User.objects.filter(application__status=Application.STATUS_ATTENDED).distinct().get(qr_code=qr_code)
        except User.DoesNotExist:
            return JsonResponse({'errors': ['Attended user not found with QRCode: %s.' % qr_code]}, status=400)
        entries = Eaten.objects.all().filter(user_id=user.id, meal_id=meal.id).order_by('-time')
        last_entry = entries.first()
        n_times_eaten = entries.count()
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
        if last_entry is not None and last_entry.time > five_minutes_ago:
            return JsonResponse({'errors': ['User has just ate 5 minutes ago!']}, status=400)
        if n_times_eaten >= meal.times:
            return JsonResponse({'errors': ['This user has already eaten %s time%s!' %
                                            (n_times_eaten, 's' if n_times_eaten > 1 else '')]}, status=400)
        # Create a new entry
        eaten = Eaten(user_id=user.id, meal_id=meal.id)
        eaten.save()
        return JsonResponse({
            'diet': user.get_diet_display(), 'other_diet': user.other_diet, 'times_eaten': n_times_eaten + 1,
            'meals_max_times': meal.times, 'full_name': user.get_full_name(), 'diet_code': user.diet
        })
