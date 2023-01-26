from django.urls import path

from event.messages import views

urlpatterns = [
    path('', views.AnnouncementList.as_view(), name='announcement_list'),
    path('new/', views.AnnouncementFormView.as_view(), name='new_announcement'),
    path('<int:aid>/', views.AnnouncementFormView.as_view(), name='edit_announcement'),
]
