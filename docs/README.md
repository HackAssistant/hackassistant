# Documentation

Here is the full documentation for the project at the moment. We have divided it into two types: documentation for 
configuration and documentation for development utilities.

<details><summary>

## Configuration
</summary>

This configurations will be divided in application configurations and libraries configurations.

<details><summary>

### Apps
</summary>

[//]: # (Stats, User, Event, Application, Meals, Review, Messages)

- **[Friends](configuration/friends.md)**: This optional app enables the participants to apply with their friends and then for the organizers to group their applications 
in order to invite all the friends.

</details>

<details><summary>

### Libraries
</summary>

- **[Admin honeypot](configuration/admin_honeypot.md)**: Fake Django admin login screen to log and notify admins of attempted unauthorized access.
- **[Allauth](configuration/allauth.md)**: Integrated set of Django applications addressing authentication, registration, account management as well as 
3rd party (social) account authentication.
- **[Axes](configuration/axes.md)**: Axes is a Django plugin for keeping track of suspicious login attempts for your Django based website and implementing simple brute-force attack blocking.
- **[Captcha](configuration/captcha.md)**: Django reCAPTCHA form field/widget integration app.
- **[Colorfield](configuration/colorfield.md)**: Simple color field for your models with a nice color-picker in the admin-interface.
- **[Compressor](configuration/compressor.md)**: Compresses linked and inline JavaScript or CSS into a single cached file.
- **[Cors headers](configuration/corsheaders.md)**: A Django App that adds Cross-Origin Resource Sharing (CORS) headers to responses.
- **[Crontab](configuration/crontab.md)**: Dead simple crontab powered job scheduling for django.
- **[Django Bootstrap 5](configuration/django_filter.md)**: Bootstrap 5 for Django.
- **[Django CSP](configuration/django_csp.md)**: Adds Content-Security-Policy headers to Django applications.
- **[Django filter](configuration/django_filter.md)**: It allows users to filter down a queryset based on a model’s fields, displaying the form to let them do this.
- **[Django JWT](configuration/django_jwt_oidc.md)**: Django library that implements the authentication for OpenId SSO with JWT from oauth2.
- **[Django password validator](configuration/django_password_validators.md)**: Additional libraries for validating passwords in Django 2.2.25 or later.
- **[Django tables 2](configuration/django_tables2.md)**: An app for creating HTML tables.

</details>
</details>

<details><summary>

## Development utilities
</summary>

This utilities will be divided in generic utilities and app specific utilities.

<details><summary>

### Generic 
</summary>

[//]: # (Email, Utils.py, Nav, Theme, Tables, Singleton, Timezone)

- **[BootstrapFormMixin](utility/bootstrap_form_mixin.md)**: A utility to assist in the rendering of a form using Bootstrap 5.
- **[TabsViewMixin](utility/tabs_view_mixin.md)**: A utility to help the creation of necessary methods for displaying a view with tabs, which will automatically render when used in your views.
- **[PermissionRequiredMixin](utility/permission_required_mixin.md)**: Improvement of the Django PermissionRequiredMixin class. Inherit this if you create new permission mixins please.

</details>

<details><summary>

### App specific
</summary>

#### Application

- **[Application Forms](utility/application_form.md)**: Generic class to create types of applications (Hacker, Mentor, etc.) that integrates automatically the forms with the Application Model.

#### Event.Messages
 
- **[MessageServiceManager](utility/messages.md)**: Explanation of how this services work and how to use it to send quick messages to the participants.

</details>

</details>

<style>
details summary > * {  
    display: inline; 
}
details {
    margin-top: 25px;
}
</style>
