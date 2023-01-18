from django.urls import path, include

from app.utils import is_installed
from event import views


urlpatterns = [
    path('checkin/', views.CheckinList.as_view(), name='checkin_list'),
    path('checkin/admin/', views.CheckinAdminList.as_view(), name='checkin_list_admin'),
    path('checkin/<str:uid>/', views.CheckinUser.as_view(), name='checkin_user'),
]

if is_installed('event.messages'):
    urlpatterns.append(path('announcements/', include('event.messages.urls')))

if is_installed('event.meals'):
    urlpatterns.append(path('', include('event.meals.urls')))
