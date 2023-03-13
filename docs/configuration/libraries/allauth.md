# Django-allauth [+](https://django-allauth.readthedocs.io/en/latest/)

Integrated set of Django applications addressing authentication, registration, account management as well as 
3rd party (social) account authentication.

## Features

- GitHub login: Environment variables `GITHUB_CLIENT_ID` & `GITHUB_SECRET`.

## Integration to Hackassistant

Set the configurations you want on `SOCIALACCOUNT_PROVIDERS` in [`settings.py`](/app/settings.py).
In addition to the library configuration you must add the key `'ICON'` to you 3rd party configuration dictionary. 
With this the button will be added automatically to the login and register page.

## Future work

- Integrate more 3rd party social accounts
