from django.db.models.signals import pre_save, post_init
from django.dispatch import receiver

from app.utils import is_instance_on_db
from event.messages.models import Announcement


@receiver(post_init, sender=Announcement, weak=False)
def secondary_center_on_change(sender, instance: Announcement, **kwargs):
    instance.__old_sent = instance.sent or False


@receiver(pre_save, sender=Announcement, weak=False)
def inscription_on_change(sender, instance: Announcement, **kwargs):
    if (not is_instance_on_db(instance) or hasattr(instance, '__old_sent') and not instance.__old_sent) and \
            instance.sent:
        instance.send()
