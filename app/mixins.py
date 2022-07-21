import copy

from django.forms import model_to_dict
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class TabsViewMixin:
    def get_current_tabs(self):
        return []

    def get_back_url(self):
        return None

    def get_context_data(self, **kwargs):
        c = super(TabsViewMixin, self).get_context_data(**kwargs)
        c.update({'tabs': self.get_current_tabs(), 'back': self.get_back_url()})
        return c


class OverwriteOnlyModelFormMixin(object):
    '''
    Delete POST keys that were not actually found in the POST dict
    to prevent accidental overwriting of fields due to missing POST data.
    Based on:
     https://yuji.wordpress.com/2013/03/12/django-prevent-modelform-from-updating-values-if-user-did-not-submit-them/
    '''

    def clean(self):
        cleaned_data = super(OverwriteOnlyModelFormMixin, self).clean()
        c_cl_data = cleaned_data.copy()
        for field in c_cl_data.keys():
            if self.prefix is not None:
                post_key = '-'.join((self.prefix, field))
            else:
                post_key = field

            if post_key not in list(self.data.keys()) + list(self.files.keys()):
                # value was not posted, thus it should not overwrite any data.
                del cleaned_data[field]

        # only overwrite keys that were actually submitted via POST.
        model_data = model_to_dict(self.instance)
        model_data.update(cleaned_data)
        return model_data


class BootstrapFormMixin:

    # example: {'TITLE': {'fields': [{'name': 'FIELD_NAME', 'space': GRID_NUMBER},], 'description': 'DESCRIPTION'},}
    # UPPER LETTERS MUST BE CHANGED
    bootstrap_field_info = {}
    read_only = []

    def __init__(self, *args, **kwargs):
        self.make_not_required()
        super().__init__(*args, **kwargs)

    def make_not_required(self):
        bootstrap_info = self.get_bootstrap_field_info()
        bootstrap_fields = set()
        for list_fields in bootstrap_info.values():
            for field in list_fields.get('fields', []):
                bootstrap_fields.add(field.get('name'))
        for name, field in self.declared_fields.items():
            if name not in bootstrap_fields:
                field.required = False

    def get_bootstrap_field_info(self):
        return copy.deepcopy(self.bootstrap_field_info)

    def set_read_only(self):
        for field in self.fields.values():
            field.disabled = True

    @property
    def is_read_only(self):
        for field in self.fields.values():
            if not field.disabled:
                return False
        return True

    def get_fields(self):
        result = self.get_bootstrap_field_info()
        for list_fields in result.values():
            visible = {}
            for field in list_fields.get('fields', []):
                name = field.get('name')
                field.update({'field': self.fields.get(name).get_bound_field(self, name)})
                visible[field['field'].auto_id] = {
                    self.fields.get(visible_name).get_bound_field(self, visible_name).html_name:
                        ([str(x) for x in values] if isinstance(values, list) else [str(values)])
                    for visible_name, values in field.get('visible', {}).items()
                }
                if field['field'].field.required:
                    field['field'].label = mark_safe(field['field'].label + ' <span class="text-danger">*</span>')
                api_fields = getattr(getattr(self, 'Meta', None), 'api_fields', {})
                if name in api_fields:
                    field['api'] = api_fields[name]
                    if field['api'].get('restrict', False):
                        field['field'].help_text += _("Please select one of the dropdown options or write 'Others'.")
                if not visible[field['field'].auto_id]:
                    del visible[field['field'].auto_id]
            list_fields['visible'] = visible
        return result
