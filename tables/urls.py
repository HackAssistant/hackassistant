from django.urls import path

from tables import views

urlpatterns = [
    path('', views.TablesHome.as_view(), name='tables_home'),
    path('model/<str:model>/', views.ModelTableView.as_view(), name='model_table'),
]
