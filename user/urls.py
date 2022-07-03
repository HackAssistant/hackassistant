from django.urls import path

from user import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path('register/', views.Register.as_view(), name='register'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('needs_verification/', views.NeedsVerification.as_view(), name='needs_verification'),
    path('verify_email/<str:uid>/<str:token>/', views.VerifyEmail.as_view(), name='verify_email'),
    path('forgot_password/', views.ForgotPassword.as_view(), name='forgot_password'),
    path('password_reset/<str:uid>/<str:token>/', views.ChangePassword.as_view(), name='password_reset'),
]
