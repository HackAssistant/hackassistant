import re

from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from app.mixins import BootstrapFormMixin
from user.models import User
from django.utils.translation import gettext_lazy as _


class LoginForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {'fields': [{'name': 'email', 'space': 12}, {'name': 'password', 'space': 12}]}}

    email = forms.EmailField(label=_('Email'), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'), max_length=100)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email.lower()

    def reset_status_fields(self):
        self.add_error('email', '')
        self.add_error('password', '')


class UserCreationForm(BootstrapFormMixin, forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    bootstrap_field_info = {'': {'fields': [{'name': 'first_name', 'space': 6}, {'name': 'last_name', 'space': 6},
                                            {'name': 'email', 'space': 12}, {'name': 'password1', 'space': 12},
                                            {'name': 'password2', 'space': 12}]}}

    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput,
                                help_text=' '.join(password_validation.password_validators_help_texts()))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        regex_organizer_email = getattr(settings, 'REGEX_HACKATHON_ORGANIZER_EMAIL', None)
        organizer_emails = getattr(settings, 'HACKATHON_ORGANIZER_EMAILS', [])
        if commit:
            user.save()
            if regex_organizer_email and re.match(regex_organizer_email, user.email) or user.email in organizer_emails:
                user.set_organizer()
        return user


class RegistrationForm(UserCreationForm):
    bootstrap_field_info = {'': {'fields': [{'name': 'first_name', 'space': 6}, {'name': 'last_name', 'space': 6},
                                            {'name': 'email', 'space': 12}, {'name': 'password1', 'space': 12},
                                            {'name': 'password2', 'space': 12},
                                            {'name': 'terms_and_conditions', 'space': 12},
                                            {'name': 'email_subscribe', 'space': 12}]}}

    terms_and_conditions = forms.BooleanField(
        label=mark_safe(_('I\'ve read, understand and accept <a href="/privacy_and_cookies" target="_blank">HackUPC '
                          'Privacy and Cookies Policy</a>.')))

    def clean_password2(self):
        password2 = super().clean_password2()
        password_validation.validate_password(password2)
        return password2

    def clean_terms_and_conditions(self):
        cc = self.cleaned_data.get('terms_and_conditions', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(_(
                "In order to apply and attend you have to accept our Terms & Conditions and"
                " our Privacy and Cookies Policy."
            ))
        return cc

    class Meta(UserCreationForm.Meta):
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', 'email_subscribe')
        labels = {
            'email_subscribe': _('Subscribe to our Marketing list in order to inform you about our next events.')
        }


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()
    # user_permissions = forms.ModelMultipleChoiceField(queryset=Permission.objects.filter(
    #     content_type__app_label='application'))

    class Meta:
        model = User
        fields = '__all__'


class UserProfileForm(BootstrapFormMixin, forms.ModelForm):
    bootstrap_field_info = {_('Personal Info'): {'fields': [
        {'name': 'first_name', 'space': 6}, {'name': 'last_name', 'space': 6}, {'name': 'email', 'space': 6},
        {'name': 'phone_number', 'space': 6}, {'name': 'tshirt_size', 'space': 4}, {'name': 'diet', 'space': 4},
        {'name': 'other_diet', 'space': 4, 'visible': {'diet': User.DIET_OTHER}}, {'name': 'under_age', 'space': 4},
        {'name': 'gender', 'space': 4}, {'name': 'other_gender', 'space': 4, 'visible': {'gender': User.GENDER_OTHER}},
    ],
        'description': _('Hey there, before we begin we would like to know a little more about you.')}, }

    under_age = forms.TypedChoiceField(
        required=True,
        label=_('How old are you?'),
        initial=False,
        coerce=lambda x: x == 'True',
        choices=((False, _('18 or over')), (True, _('Between 14 (included) and 18'))),
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is not None and instance._state.db is not None:  # instance in DB
            email_field = self.fields.get('email')
            email_field.widget.attrs['readonly'] = True
            email_field.help_text = _('This field cannot be modified')

    def get_bootstrap_field_info(self):
        info = super().get_bootstrap_field_info()
        instance = getattr(self, 'instance', None)
        if instance is None or instance._state.db is None:  # instance not in DB
            fields = info[_('Personal Info')]['fields']
            result = []
            for field in fields:
                if field['name'] not in self.Meta.fields_only_public:
                    if field['space'] == 4:
                        field['space'] = 6
                else:
                    field['space'] = 0
                result.append(field)
            info[_('Personal Info')]['fields'] = result
        return info

    def clean_email(self):
        instance = getattr(self, 'instance', None)
        if instance is not None and instance._state.db is not None:  # instance in DB
            return self.instance.email
        return self.cleaned_data.get('email')

    class Meta:
        model = User
        fields = ['first_name', 'email', 'last_name', 'phone_number', 'diet', 'other_diet', 'gender',
                  'other_gender', 'under_age', 'tshirt_size']
        fields_only_public = ['under_age', 'tshirt_size']
        help_texts = {
            'gender': _('This is for demographic purposes. You can skip this question if you want.'),
            'other_diet': _('Please fill here in your dietary requirements. '
                            'We want to make sure we have food for you!'),
            'origin': "Please select one of the dropdown options or write 'Others'. If the dropdown doesn't show up,"
                      " type following this schema: <strong>city, nation, country</strong>"
        }
        labels = {
            'gender': _('What gender do you identify as?'),
            'other_gender': _('Self-describe'),
            'tshirt_size': _('What\'s your t-shirt size?'),
            'diet': _('Dietary requirements'),
        }


class ForgotPasswordForm(BootstrapFormMixin, forms.Form):
    bootstrap_field_info = {'': {'fields': [{'name': 'email', 'space': 12}]}}

    email = forms.EmailField(label=_('Email'), max_length=100)


class SetPasswordForm(BootstrapFormMixin, forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    bootstrap_field_info = {'': {'fields': [{'name': 'new_password1', 'space': 12},
                                            {'name': 'new_password2', 'space': 12}]}}

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=' '.join(password_validation.password_validators_help_texts()),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The passwords do not match."))
        password_validation.validate_password(password2)
        return password2

    def save(self, user):
        password = self.cleaned_data["new_password1"]
        user.set_password(password)
        user.save()
