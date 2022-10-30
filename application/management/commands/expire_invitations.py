from django.core.management.base import BaseCommand
from django.utils import timezone

from application.emails import send_email_last_reminder, send_email_expired
from application.models import ApplicationTypeConfig, Application


class Command(BaseCommand):
    help = 'Expires all current applications that need to be expired'

    def handle(self, *args, **kwargs):
        for application_type in ApplicationTypeConfig.objects.filter(expire_invitations__gt=0):
            now = timezone.now()
            # First we set the last reminder
            diff = timezone.timedelta(days=application_type.expire_invitations - 1)
            for application in application_type.application_set.actual().filter(status=Application.STATUS_INVITED,
                                                                                status_update_date__lt=now - diff):
                application.set_status(Application.STATUS_LAST_REMINDER)
                application.save()
                send_email_last_reminder(application)
            # Lastly we set the expired
            diff = timezone.timedelta(days=1)
            for application in application_type.application_set.actual().filter(status=Application.STATUS_LAST_REMINDER,
                                                                                status_update_date__lt=now - diff):
                application.set_status(Application.STATUS_EXPIRED)
                application.save()
                send_email_expired(application)
