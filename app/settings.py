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
from django.utils import timezone

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
    'admin_honeypot',
    'captcha',
    'django_tables2',
    'django_filters',
    'django_jwt',
    'django_jwt.server',
    'django_bootstrap5',
    'compressor',
    'colorfield',
    'corsheaders',
    'django_crontab',
    'axes',
    'django_password_validators',
    'django_password_validators.password_history',
    'user',
    'application',
    'review',
    'friends',
    'event',
    'stats',
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
    'app.middlewares.TimezoneMiddleware',
    'csp.middleware.CSPMiddleware',
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
                'csp.context_processors.nonce',
            ],
            'libraries': {
                'util': 'app.templatetags.util',
                'crispy_forms_tags': 'app.templatetags.util',
            },
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite3')
DB_ENGINE = DB_ENGINE if DB_ENGINE in ['sqlite3', 'postgresql', 'mysql', 'oracle'] else 'sqlite3'

if DB_ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db' / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.%s' % DB_ENGINE,
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
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
        'NAME': 'django_password_validators.password_history.password_validation.UniquePasswordsValidator',
    },
    {
        'NAME': 'django_password_validators.password_character_requirements.password_validation.'
                'PasswordCharacterValidator',
        'OPTIONS': {
            'min_length_digit': 1,
            'min_length_alpha': 1,
            'min_length_special': 1,
            'min_length_lower': 1,
            'min_length_upper': 1,
            'special_characters': ",.-~!@#$%^&*()_+{}\":;'[]"
        }
    },
]

AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesStandaloneBackend',

    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]

# django-axes configuration
AXES_USERNAME_FORM_FIELD = 'user.models.User.USERNAME_FIELD'
AXES_COOLOFF_TIME = timezone.timedelta(minutes=5)
AXES_FAILURE_LIMIT = os.environ.get('AXES_FAILURE_LIMIT', 3)
AXES_ENABLED = os.environ.get('AXES_ENABLED', not DEBUG)
AXES_IP_BLACKLIST = os.environ.get('AXES_IP_BLACKLIST', '').split(',')
SILENCED_SYSTEM_CHECKS = ['axes.W002']

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

USE_L10N = True

# Static files (CSS, JavaScript, Images) & compressor
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
COMPRESS_OFFLINE = True
LIBSASS_OUTPUT_STYLE = 'compressed'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

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
    'CLIENT_ID': os.environ.get('OPENID_CLIENT_ID', 'client_id'),  # Required
    'TYPE': 'fake' if DEBUG else 'local',  # Required
    'RESPONSE_TYPE': 'id_token',  # Required
    'RENAME_ATTRIBUTES': {'sub': 'email', 'groups': 'get_groups'},  # Optional

}
JWT_SERVER = {
    'JWK_EXPIRATION_TIME': 3600,  # Optional
    'JWT_EXPIRATION_TIME': 14400  # Optional
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

# Google Recaptcha configuration
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '')
RECAPTCHA_WIDGET = os.environ.get('RECAPTCHA_WIDGET', 'ReCaptchaV2Checkbox')
RECAPTCHA_REGISTER = True
RECAPTCHA_LOGIN = False
try:
    RECAPTCHA_REQUIRED_SCORE = float(os.environ.get('RECAPTCHA_REQUIRED_SCORE', "0.85"))
except ValueError:
    RECAPTCHA_REQUIRED_SCORE = 0.85

# Login tries
LOGIN_TRIES = 1000 if DEBUG else 4

# Cron from Django-crontab
CRONJOBS = [
    ('0   4 * * *', 'django.core.management.call_command', ['clearsessions']),
    ('0 0 1 */6 *', 'django.core.management.call_command', ['compress', '--force']),
    ('0 */12 * * *', 'django.core.management.call_command', ['expire_invitations']),
]

# Deployment configurations for proxy pass and csrf
SECURE_HSTS_SECONDS = 2_592_000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Logging config to send logs to email automatically
LOGGING = {
    'version': 1,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'admin_email': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'app.log.HackathonDevEmailHandler',
        },
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'handlers': ['admin_email'],
        },
    },
}

# Sendgrid API key
SENDGRID_API_KEY = os.environ.get('SENDGRID_KEY', None)

# SMTP
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = os.environ.get('EMAIL_PORT', None)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
ADMINS_EMAIL = os.environ.get('ADMINS_EMAIL', '').split(',')
try:
    ADMINS.extend([(email.split('@')[0].replace('.', ' ').title(), email) for email in ADMINS_EMAIL])
except:
    pass

# Load filebased email backend if no Sendgrid credentials and debug mode
if not SENDGRID_API_KEY and not EMAIL_HOST and DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
    EMAIL_FILE_PATH = 'tmp/email-messages/'
else:
    if SENDGRID_API_KEY:
        EMAIL_BACKEND = "sgbackend.SendGridBackend"
    else:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Logging system
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
        }
    }

SESSION_COOKIE_AGE = 86400

# Cache system
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

# Content-Security-Policy
CSP_DEFAULT_SRC = ["'self'", "www.w3.org", "data:", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"]
CSP_FRAME_SRC = ['www.google.com']
CSP_SCRIPT_SRC = ["'self'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com", "code.jquery.com", "d3js.org",
                  "www.google.com", "www.gstatic.com", "'unsafe-inline'"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "cdnjs.cloudflare.com", "cdn.jsdelivr.net"]

# Securing Admin Page
ADMIN_URL = os.environ.get('ADMIN_URL', 'secret/')

# Security
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
