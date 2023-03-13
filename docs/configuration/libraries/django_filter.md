# Django-filter [+](https://django-filter.readthedocs.io/en/stable/index.html)

Django-filter is a generic, reusable application to alleviate writing some of the more mundane bits of view code. Specifically, it allows users to filter down a queryset based on a model’s fields, displaying the form to let them do this.

## Features

- Can filter APIs and tables from the [Django tables 2](django_tables2.md)

## Integration to Hackassistant

- Integrated this with the [BootstrapFormMixin](../../utility/generic/bootstrap_form_mixin.md) for rendering the filters forms with Boostrap 5.
- Need to create a Form for setting the BootstrapFormMixin settings and then add the form to the Filter class.

## Future work

- More filters.
