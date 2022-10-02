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
