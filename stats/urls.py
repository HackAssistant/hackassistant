from django.urls import path

from stats import views

urlpatterns = [
    path('', views.StatsHome.as_view(), name='stats_home'),
    path('<str:model>/', views.StatsView.as_view(), name='stats'),
    path('<str:model>/data/', views.StatsDataView.as_view(), name='stats_data'),
]
