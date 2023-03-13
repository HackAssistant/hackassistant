import random

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.utils import is_installed, announcement
from application.models import Application, Edition
from event.meals.filters import MealsTableFilter
from event.meals.forms import MealForm
from event.meals.tables import MealsTable, CheckinMealTable
from event.meals.models import Meal, Eaten
from django.http import JsonResponse
from application.mixins import PermissionRequiredMixin

from user.models import User


class MealsList(PermissionRequiredMixin, SingleTableMixin, TemplateView):
    permission_required = 'event.can_checkin_meal'
    template_name = 'meals_list.html'
    table_class = MealsTable

    def get_queryset(self):
        return Meal.objects.all()


class MealFormView(PermissionRequiredMixin, TemplateView):
    permission_required = 'event.create_meal'
    template_name = 'meal_form.html'
    announcement_templates = [
        'Exciting news: you can now enjoy %s times more of your favorite food at the meals area!',
        'Attention food lovers! Indulge in %s times more deliciousness at the meals area!',
        'Experience a gastronomical journey like never before with %s times more food at the meals area!',
        'Satisfy your cravings with %s times more delicious food at the meals area!',
    ]

    def get_permission_required(self):
        if self.kwargs.get('mid', None) is not None:
            return 'event.edit_meal'
        return super().get_permission_required()

    def get_object_instance(self):
        meal_id = self.kwargs.get('mid', None)
        if meal_id is not None:
            return get_object_or_404(Meal, id=meal_id)
        return meal_id

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meal = kwargs.get('meal', None)
        if meal is None:
            meal = self.get_object_instance()
        form = MealForm(instance=meal)
        context.update({'form': form, 'meal': meal, 'announcement_enabled': is_installed('event.messages')})
        return context

    def post(self, request, *args, **kwargs):
        meal = self.get_object_instance()
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            meal = form.save()
            if request.POST.get('announcement', None) == 'true':
                announcement(random.choice(self.announcement_templates) % meal.times)
            return redirect('meals_list')
        context = self.get_context_data(meal=meal)
        context.update({'form': form})
        return self.render_to_response(context)


class CheckinMeal(PermissionRequiredMixin, SingleTableMixin, FilterView):
    template_name = 'checkin_meal.html'
    permission_required = 'event.can_checkin_meal'
    table_class = CheckinMealTable
    filterset_class = MealsTableFilter

    def handle_no_permission(self):
        if self.request.method == 'POST':
            if not self.request.user.is_authenticated:
                return JsonResponse({'errors': ['Unauthorized, you are not logged in.']}, status=401)
            return JsonResponse({'errors': ['You have no permissions.']}, status=403)
        return super().handle_no_permission()

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
