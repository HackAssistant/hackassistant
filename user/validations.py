import requests
from django.conf import settings
from django.core.exceptions import ValidationError


def disposable_email(email):
    token = getattr(settings, 'DISPOSABLE_EMAIL_TOKEN', None)
    if token is not None:
        url = "https://api.testmail.top/domain/check"
        email_domain = email.split('@')[1]
        headers = {
            'Authorization': 'Bearer %s' % token
        }
        response = requests.request("GET", url, headers=headers, params={"data": email_domain})
        result = response.json()
        if not result["result"]:
            raise ValidationError('Disposable emails are not permitted.')
