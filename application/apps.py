import inspect
import sys

from django.apps import AppConfig
from django.core.signals import request_finished
from django.utils import timezone


class ApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'application'

    def auto_create_application_types(self):
        from application.forms import ApplicationForm
        from django.contrib.auth.models import Group

        ApplicationTypeConfig = self.get_model('ApplicationTypeConfig')
        organizer_group = Group.objects.get_or_create(name='Organizer')[0]

        for name, obj in inspect.getmembers(sys.modules['application.forms']):
            if inspect.isclass(obj) and issubclass(obj, ApplicationForm) and obj != ApplicationForm:
                type_name = name.split('Form')[0]
                Group.objects.get_or_create(name=type_name)
                ApplicationTypeConfig.objects.get_or_create(name=type_name, defaults={
                    'group_id': organizer_group.pk,
                    'end_application_date': timezone.now() + timezone.timedelta(days=300)})

    def create_permissions(self):
        from django.contrib.auth.models import Permission
        from application.models import ApplicationTypeConfig
        application_types = ApplicationTypeConfig.objects.all()
        application_permissions = Permission.objects.filter(content_type__app_label='application',
                                                            content_type__model='application')
        for application_type in application_types:
            application_permissions = application_permissions\
                .exclude(codename__endswith=application_type.name.lower())
        for application_permission in application_permissions:
            for application_type in application_types:
                Permission.objects.get_or_create(
                    codename='%s_%s' % (application_permission.codename, application_type.name.lower()),
                    defaults={'name': application_permission.name + ' ' + application_type.name.lower(),
                              'content_type': application_permission.content_type})

    def ready(self):
        try:
            self.auto_create_application_types()
            self.create_permissions()
        except:
            pass
        from . import signals
