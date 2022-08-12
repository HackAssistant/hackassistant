from django.urls import path

from review import views

urlpatterns = [
    path('', views.ApplicationReview.as_view(), name='application_review'),
    path('application/', views.ApplicationList.as_view(), name='application_list'),
    path('application/<str:uuid>/', views.ApplicationDetail.as_view(), name='application_detail'),
    path('application/<str:uuid>/logs/', views.ApplicationLogs.as_view(), name='application_logs'),
    path('application/comment', views.CommentSubmit.as_view(), name='new_comment'),
    path('application/comment/<int:log_id>/', views.CommentSubmit.as_view(), name='edit_comment'),
]
