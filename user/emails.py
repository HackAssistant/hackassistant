from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from app.emails import Email
from user.tokens import AccountActivationTokenGenerator


def send_verification_email(request, user):
    token = AccountActivationTokenGenerator().make_token(user)
    uuid = urlsafe_base64_encode(force_bytes(user.pk))
    url = request.build_absolute_uri(reverse('verify_email', kwargs={'uid': uuid, 'token': token}))
    context = {
        'user': user,
        'url': url,
    }
    Email(name='verify_email', context=context, to=user.email, request=request).send()


def send_password_reset_email(request, user):
    token = PasswordResetTokenGenerator().make_token(user)
    uuid = urlsafe_base64_encode(force_bytes(user.pk))
    url = request.build_absolute_uri(reverse('password_reset', kwargs={'uid': uuid, 'token': token}))
    print(url)
    context = {
        'user': user,
        'url': url,
    }
    Email(name='password_reset', context=context, to=user.email, request=request).send()
