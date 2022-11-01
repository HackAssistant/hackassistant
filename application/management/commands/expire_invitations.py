import re

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from application.emails import send_email_last_reminder, send_email_expired
from application.models import ApplicationTypeConfig, Application, ApplicationLog
from user.models import User


class Command(BaseCommand):
    help = 'Expires all current applications that need to be expired'

    def handle(self, *args, **kwargs):
        for application_type in ApplicationTypeConfig.objects.filter(expire_invitations__gt=0):
            now = timezone.now()
            server_email = re.search('(?<=<).+?(?=>)', getattr(settings, 'SERVER_EMAIL', ''))
            user = None
            if server_email is not None:
                user = User.objects.get_or_create(email=server_email.group(), defaults={
                    'is_active': False, 'first_name': 'Server', 'last_name': 'Cron'})[0]
            # First we set the last reminder
            diff = timezone.timedelta(days=application_type.expire_invitations - 1)
            for application in application_type.application_set.actual().filter(status=Application.STATUS_INVITED,
                                                                                status_update_date__lt=now - diff):
                log = ApplicationLog(application=application, user=user, name='Last reminder')
                old_status = application.get_status_display()
                application.set_status(Application.STATUS_LAST_REMINDER)
                log.changes = {'status': {'old': old_status, 'new': application.get_status_display()}}
                application.save()
                if user is not None:
                    log.save()
                send_email_last_reminder(application)
            # Lastly we set the expired
            diff = timezone.timedelta(days=1)
            for application in application_type.application_set.actual().filter(status=Application.STATUS_LAST_REMINDER,
                                                                                status_update_date__lt=now - diff):
                log = ApplicationLog(application=application, user=user, name='Expired')
                old_status = application.get_status_display()
                application.set_status(Application.STATUS_EXPIRED)
                log.changes = {'status': {'old': old_status, 'new': application.get_status_display()}}
                application.save()
                if user is not None:
                    log.save()
                send_email_expired(application)
