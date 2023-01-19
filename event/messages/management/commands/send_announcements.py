from django.core.management.base import BaseCommand
from django.utils import timezone

from event.messages.models import Announcement


class Command(BaseCommand):
    help = 'Send announcements from the database'

    def handle(self, *args, **kwargs):
        for announcement in Announcement.objects.filter(datetime__lte=timezone.now(),
                                                        status=Announcement.STATUS_PENDING):
            announcement.status = Announcement.STATUS_SENT
            announcement.save()
            announcement.send()
