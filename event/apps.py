from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event'

    def create_new_permissions(self):
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission

        from application.models import ApplicationTypeConfig

        permissions = ['can_checkin', ]

        content_type = ContentType.objects.get_or_create(app_label='event', model='event')[0]

        for permission in permissions:
            name = permission.replace('_', ' ').capitalize()
            Permission.objects.get_or_create(codename=permission, defaults={'name': 'Can checkin',
                                                                            'content_type': content_type})
            application_types = ApplicationTypeConfig.objects.all()
            for application_type in application_types:
                Permission.objects.get_or_create(
                    codename='%s_%s' % (permission, application_type.name.lower()),
                    defaults={'name': name + ' ' + application_type.name.lower(),
                              'content_type': content_type})

    def ready(self):
        try:
            self.create_new_permissions()
        except:
            pass
