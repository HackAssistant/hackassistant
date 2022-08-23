"""
Django settings for myhackupc2 project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path

from django.contrib.messages import constants as message_constants

from .hackathon_variables import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-*9+h@8wtz_f0i#0i@*8(dt#y1ktpb^1*)ddwr)su8$doq6ny1w')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'true').lower() != 'false'

ALLOWED_HOSTS = []
HOST = os.environ.get('HOST')

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
elif HOST is not None:
    ALLOWED_HOSTS.append(HOST)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_tables2',
    'django_filters',
    'django_jwt',
    'django_jwt.server',
    'django_bootstrap5',
    'corsheaders',
    'user',
    'application',
    'review',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'app' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'app.template.app_variables',
            ],
            'libraries': {
                'util': 'app.templatetags.util',
            },
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]

MEDIA_ROOT = 'files'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# App theme: dark, light, both
THEME = 'both'

# UserModel default
AUTH_USER_MODEL = 'user.User'
LOGIN_URL = '/auth/login'

# JWT settings
JWT_CLIENT = {
    'OPENID2_URL': os.environ.get('OPENID_CLIENT_ID', 'http://localhost:8000/openid'),  # Required
    'CLIENT_ID': os.environ.get('OPENID_CLIENT_ID', 'client_id'),                       # Required
    'TYPE': 'fake' if DEBUG else 'local',                                               # Required
    'RESPONSE_TYPE': 'id_token',                                                        # Required
    'RENAME_ATTRIBUTES': {'sub': 'email', 'groups': 'get_groups'},                      # Optional

}
JWT_SERVER = {
    'JWK_EXPIRATION_TIME': 3600,                # Optional
    'JWT_EXPIRATION_TIME': 14400                # Optional
}

DJANGO_TABLES2_TEMPLATE = 'django_tables2/bootstrap-responsive.html'

# Toast styles
MESSAGE_TAGS = {
    message_constants.DEBUG: 'info text-dark',
    message_constants.INFO: 'info text-dark',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning text-dark',
    message_constants.ERROR: 'danger',
}

# Google recaptcha
GOOGLE_RECAPTCHA_SECRET_KEY = os.environ.get('GOOGLE_RECAPTCHA_SECRET_KEY', '')
GOOGLE_RECAPTCHA_SITE_KEY = os.environ.get('GOOGLE_RECAPTCHA_SITE_KEY', '')

# Login tries
LOGIN_TRIES = 1000 if DEBUG else 4
