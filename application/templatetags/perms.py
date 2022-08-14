from django import template

register = template.Library()


@register.filter
def add_type(_1, _2):
    return _1, _2


@register.filter
def has_application_perm(perms, value):
    application_type_name = ''
    if isinstance(perms, tuple) or isinstance(perms, list):
        perms, application_type_name = perms
        application_type_name = '_' + application_type_name.lower()
    return perms['application'][value] or perms['application'][value + application_type_name]
