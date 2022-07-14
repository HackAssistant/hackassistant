from django.urls import path

from application import views

urlpatterns = [
    path('', views.ApplicationHome.as_view(), name='apply_home'),
    path('<str:type>/apply/', views.ApplicationApply.as_view(), name='apply'),
    path('<str:type>/apply/<str:token>/', views.ApplicationApplyPrivate.as_view(), name='apply_private'),
    path('<str:type>/<str:uuid>/', views.ApplicationEdit.as_view(), name='edit_application'),
    path('<str:uuid>/change/<str:status>/', views.ApplicationChangeStatus.as_view(), name='change_status_application'),
    path('file/<str:field>/<str:uuid>/preview/', views.ApplicationFilePreview.as_view(),
         name='application_file_preview'),
    path('file/<str:field>/<str:uuid>/', views.ApplicationFile.as_view(), name='application_file'),
]
