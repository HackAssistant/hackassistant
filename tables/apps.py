from django.apps import AppConfig


class TablesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tables'

    def create_new_permissions(self):
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth.models import Permission

        from tables.views import MODELS

        permissions = ['view_table', ]

        content_type = ContentType.objects.get_or_create(app_label='tables', model='tables')[0]

        for permission in permissions:
            name = permission.replace('_', ' ').capitalize()
            Permission.objects.get_or_create(codename=permission, defaults={'name': name,
                                                                            'content_type': content_type})
            for model in MODELS:
                Permission.objects.get_or_create(
                    codename='%s_%s' % (permission, model.lower()),
                    defaults={'name': name + ' ' + model.lower(), 'content_type': content_type})

    def ready(self):
        try:
            self.create_new_permissions()
        except:
            pass
