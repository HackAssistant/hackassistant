from django import template

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
        if text.startswith('/event/' + starts.lower()):
            return True
        return text.startswith('/' + starts.lower())
    return False


@register.simple_tag
def crispy(*args, **kwargs):
    return None
