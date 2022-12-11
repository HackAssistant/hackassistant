from django.urls import path

from event.meals import views

urlpatterns = [
    path('meals/', views.MealsList.as_view(), name='meals_list'),
    path('meals/<int:mid>/', views.CheckinMeal.as_view(), name='checkin_meal'),
]
