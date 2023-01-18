import ast

from django.db import models
from django.utils.translation import gettext_lazy as _

from event.messages.services import MessageServiceManager


class Announcement(models.Model):
    STATUS_PENDING = 'P'
    STATUS_SENT = 'S'
    STATUS_ERROR = 'E'
    STATUS = (
        (STATUS_PENDING, _('Pending')),
        (STATUS_SENT, _('Sent')),
        (STATUS_ERROR, _('Error')),
    )
    STATUS_COLOR = {
        STATUS_PENDING: 'info',
        STATUS_SENT: 'success',
        STATUS_ERROR: 'danger'
    }

    name = models.CharField(help_text=_('Name to identify the message'), blank=True, max_length=100)
    message = models.TextField()
    datetime = models.DateTimeField(help_text=_('Messages will be sent at minutes divisors by 5 only'))
    services = models.CharField(max_length=200, help_text=_('Messages will be sent to the services you select'),
                                blank=True)
    status = models.CharField(choices=STATUS, max_length=2, default=STATUS_PENDING)
    error_message = models.CharField(blank=True, max_length=100)

    def get_status_color(self):
        return self.STATUS_COLOR.get(self.status)

    def get_status_title(self):
        if self.status == self.STATUS_ERROR:
            return self.error_message
        return False

    def get_services(self):
        try:
            return ast.literal_eval(self.services)
        except SyntaxError:
            return []

    def __str__(self):
        return self.name

    def send(self):
        def error_callback(error):
            self.status = self.STATUS_ERROR
            self.error_message = str(error)[:100]
            self.save()
        message_service = MessageServiceManager()
        message_service.make_announcement(message=self.message, sent_to_services=self.get_services(),
                                          error_callback=error_callback)
