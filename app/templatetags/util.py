from django import template
from django.urls import reverse

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def get_item(dict_item, value):
    return dict_item.get(value, None)


@register.filter
def nav_active(text, starts):
    if isinstance(text, str) and isinstance(starts, str):
        if text == reverse('file_review'):
            return starts.lower() == 'files'
        if text.startswith('/event/' + starts.lower()):
            return True
        return text.startswith('/' + starts.lower())
    return False


@register.filter
def get_type_list(app_list):
    return [app.type.name for app in app_list]


@register.simple_tag
def crispy(*args, **kwargs):
    return None


@register.filter
def percent(number_one, number_all):
    return (number_one / number_all) * 100
