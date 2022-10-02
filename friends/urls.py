from django.urls import path

from friends import views

urlpatterns = [
    path('', views.JoinFriendsView.as_view(), name='join_friends'),
]
