from django.urls import reverse
from django.utils import timezone

from app.emails import Email
from application.models import ApplicationTypeConfig


def send_dubious_email(request, application, reason, name):
    url = request.build_absolute_uri(reverse('edit_application', kwargs={'uuid': application.get_uuid}))
    now = timezone.now()
    types = ApplicationTypeConfig.objects.exclude(id=application.type_id)\
        .filter(public=True, end_application_date__gt=now)
    context = {
        'application': application,
        'organizer': request.user,
        'url': url,
        'reasons': reason.split('\n'),
        'types': types,
    }
    Email(name=name, context=context, to=application.user.email, reply_to=[request.user.email, ],
          bcc=[request.user.email, ], request=request).send()


def send_invitation_email(request, application):
    context = {
        'application': application,
        'url': request.build_absolute_uri(reverse('home')),
    }
    Email(name='application_invite', context=context, to=application.user.email, request=request).send()
