# Documentation
## BootstrapFormMixin
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

### Methods

#### get_bootstrap_field_info

If you want to dynamically change the `bootstrap_field_info` you can override this method.
It's important to not remove the initial call `super` to get a COPY of the `bootstrap_field_info` otherwise you will be overriding the full variable.
You will also need to be cautious with `ModelForm` and understanding how forms work.

#### set_read_only

This method is in order to make the form not editable. Keep in mind that you will need to disable the POST method on your view for this condition.

## Application Forms
Despite having different types of application, all of them are based in a common structure, defined in the 
`ApplicationForm` class. Then, for each type (hacker, volunteer, mentor and sponsor) specific parameters are 
added. This class inherits the `BootstrapFormMixin`, so all the features of it are available.

Each class starts with `bootstrap_field_info`, where all the fields of the form that have to be rendered are described.
First, it indicates the part of the form which will be modified (e.g. Personal Info, Hackathons,...). Then, each field 
is defined between brackets, detailing what information will be introduced (e.g. diet) and the space reserved in the 
screen. It's important to consider that the total length of a line is 12, therefore, a space of 4 would occupy 1/3 of
the line. If a field is only visible for a certain previous answer, the developer should indicate the case when it will
be shown(e.g. when diet is "Other", the applicant should specify their case.)

```python
{'name': 'diet', 'space': 4}, 
{'name': 'other_diet', 'space': 4, 'visible': {'diet': Application.DIET_OTHER}}
```

If the information that contains the field was previously specified (e.g. diet, gender), it won't require additional 
methods. However, if a new one is introduced (e.g. `under_age` in `HackerForm`), the corresponding class will include a 
method defining the type of answer, if it's required, its possible choices (which sometimes may be defined as constants 
at the beginning of the file) and the default value amongst others.

```python
under_age = forms.TypedChoiceField(
        required=True,
        label=_('How old are you?'),
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, _('18 or over')), (True, _('Between 14 (included) and 18'))),
        widget=forms.RadioSelect
    )
```
The method `exclude_save` is used to not store the information of the specified fields. The checkboxes of those fields 
have to be accepted in order to participate in the event. Therefore, once the application is submitted, this field will
always be `True`, so it's not necessary to consider that information anymore.

It's important to notice that all the text that will be printed out is surrounded by a low bash and parentheses. In 
future versions, this will allow to translate the displayed text in an easy way.

```python
label = _('How old are you?')
```

## TabsViewMixin

This is a simple Mixin to display Tab navigation on your TemplateView or any View class that inherits this class.
The navigation tabs are the navigation that is displayed on top of your template container.

### Methods

#### get_current_tabs
This method is meant to be overridden and return an array to be with tuples. The first element of the tuple will be the text of the tab and the second will be the url, those 2 are mandatory.
The 3rd is and optional variable that can be set to None to be omitted and displays a warning symbol.
Finally, the 4th variable is to set the tab to active with a boolean, if None or unset the tab will be active if the path equals the url.
Data can be passed to the method with the `get_context_data` kwargs at the super of your view.

#### get_back_url
Method that returns the url that will be updated to the context with the name `back`.

## PermissionRequiredMixin
This Mixin is mean to inherit any type of View class and expands the base [Django PermissionRequiredMixin](https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-permissionrequiredmixin-mixin) class.
The new functionality is that you can put a dictionary on the `permission_required` in order to change the permissions between the HTTP method: GET, POST, etc.
