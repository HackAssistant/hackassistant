from django.urls import path

from application import views

urlpatterns = [
    path('', views.ApplicationHome.as_view(), name='apply_home'),
    path('apply/', views.ApplicationApply.as_view(), name='apply'),
    path('<str:uuid>/', views.ApplicationEdit.as_view(), name='edit_application'),
    path('<str:uuid>/change_status/<str:status>/', views.ApplicationChangeStatus.as_view(),
         name='change_status_application'),
    path('file/<str:field>/<str:uuid>/preview/', views.ApplicationFilePreview.as_view(),
         name='application_file_preview'),
    path('file/<str:field>/<str:uuid>/', views.ApplicationFile.as_view(), name='application_file'),
    path('apply/save_draft/', views.SaveDraftApplication.as_view(), name='save_draft'),
    path('<str:uuid>/permission_slip/', views.PermissionSlipView.as_view(), name='permission_slip'),
    path('<str:uuid>/permission_slip/file/', views.PermissionSlipFile.as_view(), name='permission_slip_file'),
    path('<str:uuid>/permission_slip/template/', views.PermissionSlipTemplateFile.as_view(),
         name='permission_slip_template'),
]
