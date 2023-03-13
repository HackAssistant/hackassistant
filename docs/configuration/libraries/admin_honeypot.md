# Django-admin-honeypot [+](https://django-admin-honeypot.readthedocs.io/en/latest/)

Fake Django admin login screen to log and notify admins of attempted unauthorized access.

## Features

- Automatically notifies admins (from the `ADMINS_EMAIL` environment variable) if a user tries to enter the fake admin page.
- Real page path can be set with the `ADMIN_URL` environment variable to hide it from attackers.

## Integration to Hackassistant

- Integrated the library with configurations that can be found at the library documentation.

## Future work

- Maybe make honeypot for register page or others.
