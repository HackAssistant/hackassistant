import ast
import json
import uuid

from colorfield.fields import ColorField
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.utils import full_cache


class FileField(dict):
    def __init__(self, data, url) -> None:
        super().__init__()
        self.update(data)
        self.url = url

    def __str__(self) -> str:
        return self.get('path').split('/')[-1]

    def size(self):
        fs = FileSystemStorage()
        return fs.size(self.get('path'))


def get_new_order():
    max_edition = Edition.objects.order_by('-order').first()
    return max_edition.order + 1 if max_edition is not None else 0


class Edition(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(unique=True, default=get_new_order)

    def __str__(self):
        return '%s - %s' % (self.order, self.name)

    @classmethod
    @full_cache
    def get_default_edition(cls):
        return Edition.objects.order_by('-order').first().pk

    @classmethod
    @full_cache
    def get_last_edition(cls):
        try:
            return Edition.objects.order_by('-order')[1].pk
        except IndexError:
            return None


class ApplicationTypeConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_application_date = models.DateTimeField(default=timezone.now, null=True)
    end_application_date = models.DateTimeField(default=timezone.now, null=True)
    file_review_fields = models.CharField(blank=True, max_length=200, help_text=_('Activate the file fields from the '
                                                                                  'form that you want to review'))
    vote = models.BooleanField(default=True, help_text=_('Activate voting system'))
    expire_invitations = models.IntegerField(default=0, help_text=_(
        'Setting this to different to 0, sets the days that the invitation will last until expires. '
        '1 day before it expires there will be a reminder'))
    dubious = models.BooleanField(default=True, help_text=_('Dubious reviewing system'))
    blocklist = models.BooleanField(default=True, help_text=_('Applications pass test of blocklist table on apply'))
    auto_confirm = models.BooleanField(default=False, help_text=_('Applications set on status confirmed by default'))
    compatible_with_others = models.BooleanField(default=False, help_text=_('User can confirm in more than one type'))
    create_user = models.BooleanField(default=True, help_text=_('Setting this to True creates a user if it was not '
                                                                'authenticated create a user for him to enter later'))
    only_authenticated = models.BooleanField(default=False, help_text=_('Setting this to True, user will need to be '
                                                                        'authenticated tp apply'))
    hidden = models.BooleanField(default=False, help_text=_('Setting this to True doesn\'t show the application '
                                                            'to registered users'))
    token = models.UUIDField(default=uuid.uuid4)
    spots = models.PositiveIntegerField(default=100, help_text=_('Number of total spots for this type of participants. '
                                                                 'Attrition rate will be added automatically.'))

    @property
    def get_token(self):
        return str(self.token)

    def get_spots_with_attrition(self):
        return int(self.spots * getattr(settings, 'ATTRITION_RATE', 1))

    def get_description(self):
        from application import forms
        aux = forms
        lookup = ['%sForm' % self.name.title(), 'Meta', 'description']
        for item in lookup:
            aux = getattr(aux, item, None)
            if aux is None:
                return ''
        return aux

    def get_file_review_fields(self):
        try:
            return ast.literal_eval(self.file_review_fields)
        except SyntaxError:
            return []

    def vote_enabled(self):
        return self.vote and not self.auto_confirm

    def dubious_enabled(self):
        return self.dubious and not self.auto_confirm

    def __str__(self):
        return self.name

    def active(self):
        now = timezone.now()
        return self.start_application_date < now < self.end_application_date

    def closed(self):
        now = timezone.now()
        return self.end_application_date < now

    def time_left(self):
        now = timezone.now()
        if self.closed():
            return ''
        if self.active():
            left = self.end_application_date - now
        else:
            left = self.start_application_date - now
        result = ''
        days = left.days
        hours = (left.seconds - left.days * 24) // 3600
        minutes = (left.seconds % 3600) // 60
        if days > 0:
            result += ' %s %s,' % (days, _('days') if days > 1 else _('day'))
        if hours > 0:
            result += ' %s %s,' % (hours, _('hours') if hours > 1 else _('hour'))
        if minutes > 0:
            result += ' %s %s,' % (minutes, _('minutes') if minutes > 1 else _('minute'))
        return result[:-1]

    @classmethod
    @full_cache
    def get_type_files(cls):
        return list(ApplicationTypeConfig.objects.exclude(file_review_fields="")
                    .exclude(file_review_fields__isnull=True).values_list('name', flat=True))


class PromotionalCode(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True,
                            help_text=_('Use this code to the apply url as ?promotional_code=[uuid]'))
    name = models.CharField(max_length=100)
    usages = models.IntegerField()
    background_color = ColorField(default='#FFFFFF')
    color = ColorField(default='#000000')

    def __str__(self):
        return self.name

    @classmethod
    @full_cache
    def active(cls):
        return PromotionalCode.objects.count() > 0


class ApplicationQueryset(models.QuerySet):
    def actual(self):
        return self.filter(edition_id=Edition.get_default_edition())

    def convert_kwargs(self, kwargs):
        attributes = [item.attname.replace('_id', '') for item in self.model._meta.fields]
        attributes.extend(self.model._meta.fields_map.keys())
        attributes.extend(['pk', 'count'])
        new_kwargs = {}
        for key, value in kwargs.items():
            if key.split('__')[0] in attributes or key[:-3] in attributes:
                new_kwargs[key] = value
            else:
                value = json.dumps(value)
                # __ not supported on data attributes
                new_kwargs['data__icontains'] = '"%s": %s' % (key.split('__')[0], value)
        return new_kwargs

    def filter(self, *args, **kwargs):
        kwargs = self.convert_kwargs(kwargs)
        return super().filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        kwargs = self.convert_kwargs(kwargs)
        return super().exclude(*args, **kwargs)

    def invited(self):
        return self.filter(status__in=[self.model.STATUS_INVITED, self.model.STATUS_LAST_REMINDER,
                                       self.model.STATUS_CONFIRMED, self.model.STATUS_ATTENDED])


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
    STATUS_NEEDS_CHANGE = 'NC'
    STATUS_INVALID = 'IV'
    STATUS_BLOCKED = 'BL'
    STATUS = [
        (STATUS_PENDING, _('Under review')),
        (STATUS_REJECTED, _('Wait listed')),
        (STATUS_INVITED, _('Invited')),
        (STATUS_LAST_REMINDER, _('Last reminder')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_ATTENDED, _('Attended')),
        (STATUS_EXPIRED, _('Expired')),
        (STATUS_DUBIOUS, _('Dubious')),
        (STATUS_INVALID, _('Invalid')),
        (STATUS_BLOCKED, _('Blocked')),
        (STATUS_NEEDS_CHANGE, _('Needs change')),
    ]
    STATUS_COLORS = {
        STATUS_NEEDS_CHANGE: 'warning',
        STATUS_LAST_REMINDER: 'warning',
        STATUS_DUBIOUS: 'warning',
        STATUS_PENDING: 'info',
        STATUS_CONFIRMED: 'success',
        STATUS_ATTENDED: 'success',
        STATUS_INVITED: 'primary',
        STATUS_CANCELLED: 'danger',
        STATUS_EXPIRED: 'danger',
        STATUS_INVALID: 'danger',
        STATUS_REJECTED: 'danger',
        STATUS_BLOCKED: 'danger',
    }
    STATUS_DESCRIPTION = {
        STATUS_NEEDS_CHANGE: _('Your application might have some misleading information. '
                               'Please edit what the organizing team told you to.'),
        STATUS_LAST_REMINDER: _('You have been invited but not accepted yet. '
                                'In less than 24h you will lose your invitation'),
        STATUS_PENDING: _('The organizing team is reviewing your application. Please be patient.'),
        STATUS_CONFIRMED: _('You have confirmed your application. Can\'t wait seeing you in the hack!'),
        STATUS_INVITED: _('Congratulations! You have been invited, accept your invitation.'),
        STATUS_CANCELLED: _('You have cancelled your application, we hope to see you next year.'),
        STATUS_EXPIRED: _('Your application invitation have been expired. '
                          'Please contact us quick if you want to come.'),
        STATUS_INVALID: _('Your application have been invalidated. It seems you cannot join us with this role.'),
        STATUS_REJECTED: _('We are so sorry, but our hack is full...'),
        STATUS_BLOCKED: _('User was blocked by your organization.'),
        STATUS_DUBIOUS: _('This application has something suspicious'),
        STATUS_ATTENDED: _('You have arrived at the event. Have fun!'),
    }

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    type = models.ForeignKey(ApplicationTypeConfig, on_delete=models.DO_NOTHING)
    edition = models.ForeignKey(Edition, on_delete=models.RESTRICT, default=Edition.get_default_edition)

    promotional_code = models.ForeignKey(PromotionalCode, on_delete=models.SET_NULL, blank=True, null=True)

    submission_date = models.DateTimeField(default=timezone.now, editable=False)
    last_modified = models.DateTimeField(default=timezone.now)
    status_update_date = models.DateTimeField(default=timezone.now)

    status = models.CharField(choices=STATUS, default=STATUS_PENDING, max_length=2)

    data = models.TextField(blank=True)

    objects = ApplicationQueryset.as_manager()

    @property
    def form_data(self):
        result = {}
        try:
            for name, value in json.loads(self.data).items():
                if isinstance(value, dict) and value.get('type', None) == 'file':
                    result[name] = FileField(value, url=reverse(
                        'application_file_preview', kwargs={'field': name, 'uuid': self.get_uuid}))
                else:
                    result[name] = value
        except json.JSONDecodeError:
            pass
        return result

    def set_status(self, status):
        self.status = status
        self.status_changed = True
        self.status_update_date = timezone.now()

    @form_data.setter
    def form_data(self, data):
        self.data = json.dumps(data)

    def __str__(self):
        return '%s - %s: %s' % (self.edition.name, self.type.name, self.user.email)

    @property
    def get_uuid(self):
        return str(self.uuid)

    def get_public_status_display(self):
        status = self.get_public_status()
        return [y for (x, y) in self.STATUS if x == status][0]

    def get_public_status(self):
        if self.status in [self.STATUS_BLOCKED, self.STATUS_DUBIOUS]:
            return self.STATUS_PENDING
        return self.status

    def get_public_status_color(self):
        status = self.get_public_status()
        return self.STATUS_COLORS.get(status, None)

    def get_public_status_description(self):
        status = self.get_public_status()
        return self.STATUS_DESCRIPTION.get(status, '')

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status, None)

    def get_status_description(self):
        return self.STATUS_DESCRIPTION.get(self.status, '')

    def get_full_name(self):
        if self.user is not None:
            return self.user.get_full_name()
        return self.form_data.get('full_name', '')

    def to_dict(self):
        instance_dict = {x: y for x, y in self.__dict__.items() if x not in ['_state', 'data']}
        instance_dict.update(self.form_data)
        return instance_dict

    def invited(self):
        return self.status in [self.STATUS_INVITED, self.STATUS_LAST_REMINDER]

    def confirmed(self):
        return self.status in [self.STATUS_CONFIRMED, self.STATUS_ATTENDED]

    def can_edit(self):
        return self.status in [self.STATUS_PENDING, self.STATUS_NEEDS_CHANGE]

    def save(self, *args, **kwargs):
        if getattr(self, 'status_changed', False):
            self.last_modified = self.status_update_date
        else:
            self.last_modified = timezone.now()
        super().save(*args, **kwargs)

    def get_permission_slip(self, raise_404=False):
        try:
            return PermissionSlip.objects.get(user_id=self.user_id, edition_id=self.edition_id)
        except PermissionSlip.DoesNotExist:
            if raise_404:
                from django.http import Http404
                raise Http404
            return None

    class Meta:
        unique_together = ('type', 'user', 'edition')
        permissions = (
            ('can_review_application', _('Can review application')),
            ('can_invite_application', _('Can invite application')),
            ('can_review_dubious_application', _('Can review dubious application')),
            ('can_review_blocked_application', _('Can review blocked application')),
            ('can_review_files', _('Can review files')),
        )


class ApplicationLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, db_index=False, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, db_index=False)
    name = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    data = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)

    class NotFound:
        pass

    @property
    def changes(self):
        result = {}
        try:
            result.update(json.loads(self.data))
        except json.JSONDecodeError:
            pass
        return result

    @changes.setter
    def changes(self, data):
        self.data = json.dumps(data)

    def set_file_changes(self, files):
        changes = self.changes
        changes.update({field: 'New file' for field in files})
        self.changes = changes

    @classmethod
    def create_log(cls, application, user, name='Change', comment=''):
        log = cls(application=application, user=user, comment=comment, name=name)
        if name == 'Change':
            changes = {}
            old_application = Application.objects.get(pk=application.pk).to_dict()
            for field, value in application.to_dict().items():
                if value != old_application.get(field, None):
                    change = {'new': value}
                    if old_application.get(field, cls.NotFound) != cls.NotFound:
                        change['old'] = old_application[field]
                    changes[field] = change
            log.changes = changes
        return log

    def get_grouped_reactions(self):
        reactions = {}
        for reaction in self.reactions.order_by('date'):
            item = reactions.get(reaction.emoji, {'count': 0, 'users_id': {}, 'users_names': []})
            item['count'] += 1
            item['users_id'][reaction.user_id] = reaction.id
            item['users_names'].append(reaction.user.get_full_name())
            reactions[reaction.emoji] = item
        return reactions


class DraftApplicationManager(models.QuerySet):
    def get_or_create(self, defaults=None, **kwargs):
        if isinstance(defaults, dict) and defaults.get('form_data', None) is not None:
            defaults['data'] = json.dumps(defaults['form_data'])
            del defaults['form_data']
        return super().get_or_create(defaults, **kwargs)


class DraftApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    data = models.TextField(blank=True)

    objects = DraftApplicationManager.as_manager()

    @property
    def form_data(self):
        try:
            return json.loads(self.data)
        except json.JSONDecodeError:
            return {}

    @form_data.setter
    def form_data(self, new_data: dict):
        data = self.form_data
        data.update(new_data)
        self.data = json.dumps(data)


def get_permission_slip_file_name(instance, filename):
    return '%s/User/permission_slip/%s_%s.%s' % (instance.edition.name, instance.user.get_full_name().replace(' ', '-'),
                                                 instance.user.id, filename.split('.')[-1])


class PermissionSlip(models.Model):
    STATUS_ACCEPTED = 'A'
    STATUS_UPLOADED = 'U'
    STATUS_NONE = 'N'
    STATUS_DENIED = 'D'
    STATUS = (
        (STATUS_NONE, _('Missing document')),
        (STATUS_DENIED, _('Not accepted')),
        (STATUS_UPLOADED, _('On review')),
        (STATUS_ACCEPTED, _('Accepted')),
    )
    STATUS_DESCRIPTION = {
        STATUS_NONE: _('Upload the permission slip signed by your parents or legal tutors'),
        STATUS_DENIED: _('The document has been reviewed and has some problem'),
        STATUS_UPLOADED: _('Document uploaded successfully, now we will review it'),
        STATUS_ACCEPTED: _('The document has been accepted!'),
    }
    STATUS_COLORS = {
        STATUS_NONE: 'danger',
        STATUS_DENIED: 'warning',
        STATUS_UPLOADED: 'info',
        STATUS_ACCEPTED: 'success',
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    edition = models.ForeignKey(Edition, null=True, on_delete=models.SET_NULL)
    status = models.CharField(choices=STATUS, max_length=2, default=STATUS_NONE)
    file = models.FileField(upload_to=get_permission_slip_file_name, null=True)

    def __str__(self):
        return '%s - %s' % (self.edition.name, self.user.get_full_name())

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status)

    def get_status_description(self):
        return self.STATUS_DESCRIPTION.get(self.status)

    class Meta:
        permissions = (
            ('can_review_permission_slip', _('Can review permission slip')),
        )
