# Documentation
## Forms
Despite having different types of application, all of them are based in a common structure, defined in the 
`ApplicationForm` class. Then, for each type (hacker, volunteer, mentor and sponsor) specific parameters are 
added.

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
method defining the type of answer, if it's required, it's possible choices (which sometimes may be defined as constants 
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

The `Meta` class is useful to link a json file to a specific field, so the user has already some possible answers. For 
example, in this application, it has been used to list all the possible countries and avoid fake answers.

It's important to notice that all the text that will be printed out is surrounded by a low bash and parentheses. In 
future versions, this will allow to translate the displayed text in an easy way.

```python
label = _('How old are you?')
```