from django import template

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def get_item(dict_item, value):
    return dict_item.get(value, None)
