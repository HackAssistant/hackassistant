# Django-recaptcha [+](https://pypi.org/project/django-recaptcha/)

Django reCAPTCHA form field/widget integration app.

## Features

- Automatically adding captcha to public pages that could be entered with bots by setting the `RECAPTCHA_PUBLIC_KEY` & 
`RECAPTCHA_PRIVATE_KEY` environment variable.
- Supports ReCaptchaV2Checkbox, ReCaptchaV2Invisible & ReCaptchaV3 with the `RECAPTCHA_WIDGET` environment variable. (Use `RECAPTCHA_REQUIRED_SCORE` for v3. Default: 0.85)
- Can be modified for the login & register pages with the boolean environment variables `RECAPTCHA_REGISTER` & `RECAPTCHA_LOGIN`.

## Integration to Hackassistant

- Integrated the library with a django form [`RecaptchaForm`](/user/forms.py) and integrated the dark/light theme as well.
- You can use this everywhere by adding the form if the `active` class method returns `True`.

## Future work

- Add this in every public page that can fill forms with bots.
