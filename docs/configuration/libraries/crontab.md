# Django-crontab [+](https://pypi.org/project/django-crontab/)

Dead simple crontab powered job scheduling for django.

## Features

- Clearing sessions automatically [[django](https://docs.djangoproject.com/en/4.1/ref/django-admin/#django-contrib-sessions)]
- Renewing the compression of scss automatically [[compressor](compressor.md)]
- Expiring invitations of participants automatically [[application](compressor.md)]
- Sending announcements every 5 minutes [[messages](compressor.md)]

## Integration to Hackassistant

Simply create a [django management command](https://docs.djangoproject.com/en/4.1/howto/custom-management-commands/) 
and then add the command to the `CRONJOBS` variable on the [`settings.py`](/app/settings.py).

## Future work

- Integrate future cron jobs with this library.
