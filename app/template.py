from django.conf import settings
from django.urls import reverse

from app.utils import get_theme


def get_main_nav(request):
    if not request.user.is_authenticated:
        return []
    if not request.user.is_organizer():
        return [
            ('Apply', '/'),
            ('My applications', '/')
        ]
    return [
        ('Hacker', reverse('home')),
        ('Event', [
            ('Activities', '/'),
            ('Meals', '/'),
            ('HardwareLab', '/'),
            ('Baggage', '/'),
            ('CheckIn', '/'), ]
         )
    ]


def app_variables(request):
    return {
        'main_nav': get_main_nav(request),
        'app_hack': getattr(settings, 'HACKATHON_NAME'),
        'app_description': getattr(settings, 'HACKATHON_DESCRIPTION'),
        'app_author': getattr(settings, 'HACKATHON_ORG'),
        'app_name': getattr(settings, 'APP_NAME'),
        'app_socials': getattr(settings, 'HACKATHON_SOCIALS', []),
        'app_theme': getattr(settings, 'THEME') == 'both',
        'theme': get_theme(request),
        'captcha_site_key': getattr(settings, 'GOOGLE_RECAPTCHA_SITE_KEY', ''),
    }
