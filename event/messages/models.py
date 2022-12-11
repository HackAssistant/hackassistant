import ast

from django.db import models
from django.utils.translation import gettext_lazy as _

from event.messages.services import MessageServiceManager


class Announcement(models.Model):
    name = models.CharField(help_text=_('Name to identify the message'), blank=True, max_length=100)
    message = models.TextField()
    datetime = models.DateTimeField(help_text=_('Messages will be sent at minutes divisors by 5 only'))
    services = models.CharField(max_length=200, help_text=_('Messages will be sent to the services you select'))
    sent = models.BooleanField(default=False)

    def get_services(self):
        try:
            return ast.literal_eval(self.services)
        except SyntaxError:
            return []

    def __str__(self):
        return self.name

    def send(self):
        message_service = MessageServiceManager()
        message_service.make_announcement(message=self.message, sent_to_services=self.get_services())
