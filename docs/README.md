# Documentation

Here is the full documentation for the project at the moment. We have divided it into two types: documentation for 
configuring applications and documentation for development utilities.

## Configuring applications

## Development utilities

This utilities will be divided in generic utilities and app specific utilities.

### Generic 

- **[BootstrapFormMixin](utility/bootstrap_form_mixin.md)**: A utility to assist in the rendering of a form using Bootstrap 5.
- **[TabsViewMixin](utility/tabs_view_mixin.md)**: A utility to help the creation of necessary methods for displaying a view with tabs, which will automatically render when used in your views.
- **[PermissionRequiredMixin](utility/permission_required_mixin.md)**: Improvement of the Django PermissionRequiredMixin class. Inherit this if you create new permission mixins please.


### App specific

- **[Application Forms](utility/application_form.md) [Application App]**: Generic class to create types of applications (Hacker, Mentor, etc.) that integrates automatically the forms with the Application Model.
- **[MessageServiceManager](utility/messages.md) [Event.Messages App]**: Explanation of how this services work and how to use it to send quick messages to the participants.
