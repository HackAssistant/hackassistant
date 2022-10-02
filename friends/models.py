import random
import string

from django.conf import settings
from django.db import models


def get_random_string():
    # With combination of lower, upper case and numbers
    characters = string.ascii_letters + string.digits
    code_length = getattr(settings, "FRIEND_CODE_LENGTH", 13)
    return ''.join(random.choice(characters) for _ in range(code_length))


class FriendsCode(models.Model):
    code = models.CharField(default=get_random_string, max_length=getattr(settings, "FRIEND_CODE_LENGTH", 13))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
