from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from application.models import Edition, ApplicationTypeConfig, PromotionalCode


@receiver(post_delete, sender=Edition, weak=False)
@receiver(post_save, sender=Edition, weak=False)
def clear_groups(sender, instance, **kwargs):
    created = kwargs.get('created', None)
    if created is None or created:
        for application_type in ApplicationTypeConfig.objects.all().values_list('name', flat=True):
            group = Group.objects.get(name=application_type)
            group.user_set.clear()
            sender.get_default_edition(force_update=True)
            sender.get_last_edition(force_update=True)
            user_model = get_user_model()
            user_model.objects.update(qr_code='')


@receiver(post_delete, sender=ApplicationTypeConfig, weak=False)
@receiver(post_save, sender=ApplicationTypeConfig, weak=False)
def clear_file_fields(sender, instance, **kwargs):
    sender.get_type_files(force_update=True)


@receiver(post_delete, sender=PromotionalCode, weak=False)
@receiver(post_save, sender=PromotionalCode, weak=False)
def reload_active(sender, instance, **kwargs):
    sender.active(force_update=True)
