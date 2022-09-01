from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from application.models import Edition, ApplicationTypeConfig


@receiver(post_save, sender=Edition)
def clear_groups(sender, instance, created, **kwargs):
    if created:
        for application_type in ApplicationTypeConfig.objects.all().values_list('name', flat=True):
            group = Group.objects.get(name=application_type)
            group.user_set.clear()
