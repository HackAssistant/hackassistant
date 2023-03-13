from django.conf import settings
from django.core.cache import cache


def get_theme(request):
    theme_config = getattr(settings, 'THEME')
    theme = theme_config
    if theme_config == 'both':
        theme = request.COOKIES.get('theme', 'light')
    if theme not in ['light', 'dark']:
        theme = 'light'
    return theme


def full_cache(func):
    def wrapper(*args, **kwargs):
        result = cache.get(func.__qualname__)
        if result is None or kwargs.get('force_update', False):
            try:
                del kwargs['force_update']
            except KeyError:
                pass
            result = func(*args, **kwargs)
            cache.set(func.__qualname__, result, 60 * 60 * 24 * 360)
        return result
    return wrapper


def is_installed(app):
    return app in settings.INSTALLED_APPS


def is_instance_on_db(instance):
    return instance is not None and instance._state.db is not None and not instance._state.adding


def notify_user(message, user):
    if is_installed('event.messages'):
        from event.messages.services import MessageServiceManager
        return MessageServiceManager().send_message_to_user(message, user)
    return False


def announcement(message):
    if is_installed('event.messages'):
        from event.messages.services import MessageServiceManager
        return MessageServiceManager().make_announcement(message)
    return False
