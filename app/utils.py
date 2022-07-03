from django.conf import settings


def get_theme(request):
    theme_config = getattr(settings, 'THEME')
    theme = theme_config
    if theme_config == 'both':
        theme = request.COOKIES.get('theme', 'light')
    if theme not in ['light', 'dark']:
        theme = 'light'
    return theme
