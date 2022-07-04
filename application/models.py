import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Application(models.Model):
    STATUS_PENDING = 'P'
    STATUS_REJECTED = 'R'
    STATUS_INVITED = 'I'
    STATUS_LAST_REMINDER = 'LR'
    STATUS_CONFIRMED = 'C'
    STATUS_CANCELLED = 'X'
    STATUS_ATTENDED = 'A'
    STATUS_EXPIRED = 'E'
    STATUS_DUBIOUS = 'D'
    STATUS_INVALID = 'IV'
    STATUS_BLACKLISTED = 'BL'
    STATUS = [
        (STATUS_PENDING, 'Under review'),
        (STATUS_REJECTED, 'Wait listed'),
        (STATUS_INVITED, 'Invited'),
        (STATUS_LAST_REMINDER, 'Last reminder'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_ATTENDED, 'Attended'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_DUBIOUS, 'Dubious'),
        (STATUS_INVALID, 'Invalid'),
        (STATUS_BLACKLISTED, 'Blacklisted')
    ]

    GENDER_NO_ANSWER = 'NA'
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_NON_BINARY = 'NB'
    GENDER_OTHER = 'X'
    GENDERS = [
        (GENDER_NO_ANSWER, 'Prefer not to answer'),
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_NON_BINARY, 'Non-binary'),
        (GENDER_OTHER, 'Prefer to self-describe'),
    ]

    TYPE_VOLUNTEER = 'V'
    TYPE_HACKER = 'H'
    TYPE_MENTOR = 'M'
    TYPE_SPONSOR = 'S'
    TYPES = (
        (TYPE_VOLUNTEER, 'Volunteer'),
        (TYPE_HACKER, 'Hacker'),
        (TYPE_MENTOR, 'Mentor'),
        (TYPE_SPONSOR, 'Sponsor'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)

    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)

    submission_date = models.DateTimeField(default=timezone.now, editable=False)
    status_update_date = models.DateTimeField(default=timezone.now)

    status = models.CharField(choices=STATUS, default=STATUS_PENDING, max_length=2)

    gender = models.CharField(max_length=23, choices=GENDERS, default=GENDER_NO_ANSWER)
    other_gender = models.CharField(max_length=50, blank=True, null=True)

    under_age = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_changed = False

    def __str__(self):
        return self.user.email

    @property
    def get_uuid(self):
        return str(self.uuid)

    def get_public_status(self):
        if self.status in [self.STATUS_BLACKLISTED, self.STATUS_DUBIOUS]:
            return [y for (x, y) in self.status if x == self.STATUS_PENDING][0]
        return self.get_status_display()

    def set_status(self, status):
        self.status = status
        self.status_changed = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.status_changed:
            self.status_update_date = timezone.now()
        super().save(force_insert, force_update, using, update_fields)
