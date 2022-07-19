import inspect
import sys

from django.apps import AppConfig
from django.utils import timezone


class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application'

    def ready(self):
        from application.forms import ApplicationForm
        from django.contrib.auth.models import Group

        ApplicationTypeConfig = self.get_model('ApplicationTypeConfig')
        group = Group.objects.get_or_create(name='Organizer')[0]

        for name, obj in inspect.getmembers(sys.modules['application.forms']):
            if inspect.isclass(obj) and issubclass(obj, ApplicationForm) and obj != ApplicationForm:
                type_name = name.split('Form')[0]
                ApplicationTypeConfig.objects.get_or_create(name=type_name, defaults={
                    'group_id': group.pk, 'end_application_date': timezone.now() + timezone.timedelta(days=300)})
