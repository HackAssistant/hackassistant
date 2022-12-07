from django.conf import settings
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
