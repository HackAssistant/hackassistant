# TimezoneMiddleware [+](/app/middlewares.py)

Django middleware that gets the timezone of the request.
Since Django can't automatically detect what the user's timezone is, I had the idea of saving the user's timezone in a 
cookie with JS on the landing page.

[Source](https://stackoverflow.com/questions/65180818/how-to-get-the-current-user-time-zone-django/73956012#73956012) 
