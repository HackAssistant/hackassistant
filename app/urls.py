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

from app.views import BaseView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', BaseView.as_view(), name='home'),
    path('auth/', include('user.urls')),
]

# JWT fake login on DEBUG for development purposes
if getattr(settings, 'DEBUG', True):
    urlpatterns.append(path('openid/', include('django_jwt.urls')))
else:
    urlpatterns.append(path('openid/', include('django_jwt.server.urls')))
