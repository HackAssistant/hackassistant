from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event.messages'
    label = 'event_messages'

    def ready(self):
        pass
