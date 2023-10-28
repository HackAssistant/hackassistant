from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from app.emails import Email


def send_email_to_blocked_admins(request, users, application, blocked_user):
    url = request.build_absolute_uri(reverse('change_status_application', kwargs={
        'uuid': application.get_uuid, 'status': application.STATUS_PENDING
    }))
    context = {
        'application': application,
        'blocked_user': blocked_user,
        'url': url,
    }
    Email(name='new_blocked', context=context, to=users, request=request).send()


def get_email_last_reminder(application):
    context = {
        'application': application,
        'url': 'https://' + str(settings.HOST) + reverse('home'),
        'app_hack': getattr(settings, 'HACKATHON_NAME'),
    }
    return Email(name='application_last_reminder', context=context, to=application.user.email)


def get_email_expired(application):
    context = {
        'application': application,
        'app_hack': getattr(settings, 'HACKATHON_NAME'),
        'app_contact': getattr(settings, 'HACKATHON_CONTACT_EMAIL', ''),
    }
    return Email(name='application_expired', context=context, to=application.user.email)


def send_email_permission_slip_upload(request, application):
    url = request.build_absolute_uri(reverse('permission_slip', kwargs={'uuid': application.get_uuid}))
    context = {
        'user': application.user,
        'url': url,
    }
    permission_slip_managers = (get_user_model().objects.with_perm('application.can_review_permission_slip')
                                .value_list('email', flat=True))
    Email(name='permission_slip_upload', context=context, to=permission_slip_managers, request=request).send()


def send_email_permission_slip_review(request, application, permission_slip):
    url = request.build_absolute_uri(reverse('permission_slip', kwargs={'uuid': application.get_uuid}))
    context = {
        'user': application.user,
        'permission_slip': permission_slip,
        'url': url,
    }
    Email(name='permission_slip_review', context=context, to=application.user.email, request=request).send()
