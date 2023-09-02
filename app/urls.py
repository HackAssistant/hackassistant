"""myhackupc2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from app import views
from app.utils import is_installed

urlpatterns = [
    path('', views.BaseView.as_view(), name='home'),
    path('legal_notice/', views.LegalNotice.as_view(), name='legal_notice'),
    path('terms_and_conditions/', views.TermsConditions.as_view(), name='terms_and_conditions'),
    path('privacy_and_cookies/', views.PrivacyCookies.as_view(), name='privacy_and_cookies'),

    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('openid/', include('django_jwt.urls')),
    path(getattr(settings, 'ADMIN_URL', 'secret/'), admin.site.urls),
    path('auth/', include('user.urls')),
    path('application/', include('application.urls')),
    path('review/', include('review.urls')),
    path('event/', include('event.urls')),
    path('stats/', include('stats.urls')),
    path('tables/', include('tables.urls')),
    path('accounts/', include('allauth.urls')),
]

if is_installed("friends"):
    urlpatterns.append(path('friends/', include('friends.urls')))

if is_installed("reimbursment"):
    urlpatterns.append(path('reimbursment/', include('reimbursment.urls')))

# Error handlers
handler404 = "app.views.handler_error_404"
handler500 = "app.views.handler_error_500"
handler403 = "app.views.handler_error_403"
handler400 = "app.views.handler_error_400"
