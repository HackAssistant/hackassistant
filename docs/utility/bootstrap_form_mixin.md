# BootstrapFormMixin [+](/app/mixins.py)
BootstrapFormMixin is a class that allows an easy way to render any form type.

At the start of the class you will need to override the `bootstrap_field_info` where all the render information is stored.
```python
bootstrap_field_info = {'TITLE': {
    'fields': [{'name': 'FIELD_NAME', 'space': GRID_NUMBER, 'visible': VALUE_DICT},], 
    'description': 'DESCRIPTION'},}
```
In this example the TITLE will be the h2 text of the formset that will contain all the fields on the array.
The description is an optional text to be displayed after the TITLE.
The FIELD_NAME will be the names of the fields of your form, this is required.
GRID_NUMBER will be the grid (1-12) space that will fill your field in the Bootstrap row, if omitted the space will be 0.
Lastly, the VALUE_DICT refers to a dictionary that will tell your field when can be visible, if omitted the field will always be visible.
IMPORTANT: if you miss a field on the `bootstrap_field_info` it will set to not required.

An important feature of this form, is the use of the TypeHead lib for autocomplete CharFields, so the user has already some possible answers.
This can be done by adding the `api_fields` .
This information is stored in the `api_fields` to the Meta class inside your form, where the API url is required. Other optional fields are `restrict` and 
`others` field to restrict the options of the field or add the Others option. For example, in this application, 
it has been used to list all the possible countries and avoid custom answers.

```python
class Meta(ApplicationForm.Meta):
    api_fields = {
        'country': {'url': static('data/countries.json'), 'restrict': True, 'others': True},
        'university': {'url': static('data/universities.json')},
        'degree': {'url': static('data/degrees.json')},
    }
```

## Methods

### get_bootstrap_field_info

If you want to dynamically change the `bootstrap_field_info` you can override this method.
It's important to not remove the initial call `super` to get a COPY of the `bootstrap_field_info` otherwise you will be overriding the full variable.
You will also need to be cautious with `ModelForm` and understanding how forms work.

### set_read_only

This method is in order to make the form not editable. Keep in mind that you will need to disable the POST method on your view for this condition.
