# Utils.py [+](/app/utils.py)

Utils.py is a python file with some util functions for the whole app.

## get_theme

Function that returns the theme from a request. Theme can be light or dark depending if both themes are activated on settings.py.

## full_cache

A Python decorator that caches the result of a function/method until the `force_update` keyword argument is passed in the function call.
## is_installed

Ideally almost all django applications can be disabled just by removing them from the `INSTALLED_APPS` on the `settings.py`.
This functions returns `True` if an application is installed or not. Use this please.

## is_instance_on_db

Functions that returns `True` if a model instance is on the BD or not.

## notify_user

Function created for adapting the [MessageServiceManager](../app_specific/messages.md) into other apps. Just call it 
with the user and message and will send a message to Slack & other services you have enabled.
