from django.contrib import admin

from event.meals.models import Meal, Eaten

admin.site.register(Meal)
admin.site.register(Eaten)
