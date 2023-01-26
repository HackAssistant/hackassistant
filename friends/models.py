import random
import string

from django.conf import settings
from django.db import models

from application.models import Application, Edition


def get_random_string():
    # With combination of lower, upper case and numbers
    characters = string.ascii_letters + string.digits
    code_length = getattr(settings, "FRIEND_CODE_LENGTH", 13)
    return ''.join(random.choice(characters) for _ in range(code_length))


class FriendsCode(models.Model):
    code = models.CharField(default=get_random_string, max_length=getattr(settings, "FRIEND_CODE_LENGTH", 13))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    STATUS_NOT_ALLOWED_TO_JOIN_TEAM = [Application.STATUS_CONFIRMED,
                                       Application.STATUS_INVITED,
                                       Application.STATUS_ATTENDED]

    def get_members(self):
        return FriendsCode.objects.filter(code=self.code)

    def is_closed(self):
        edition_pk = Edition.get_default_edition()
        return FriendsCode.objects.filter(
            code=self.code,
            user__application_set__edition_id=edition_pk,
            user__application_set__status__in=self.STATUS_NOT_ALLOWED_TO_JOIN_TEAM
        ).exists()

    def reached_max_capacity(self):
        friends_max_capacity = getattr(settings, 'FRIENDS_MAX_CAPACITY', None)
        if friends_max_capacity is not None and isinstance(friends_max_capacity, int):
            return FriendsCode.objects.filter(code=self.code).count() >= friends_max_capacity
        return False
