from django.urls import path

from event.meals import views

urlpatterns = [
    path('meals/', views.MealsList.as_view(), name='meals_list'),
    path('meals/<int:mid>/', views.CheckinMeal.as_view(), name='checkin_meal'),
    path('meals/<int:mid>/edit/', views.MealFormView.as_view(), name='edit_meal'),
    path('meals/create/', views.MealFormView.as_view(), name='create_meal'),
]
