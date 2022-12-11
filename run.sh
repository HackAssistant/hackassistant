service cron start
python manage.py crontab add
gunicorn -b 0.0.0.0:8000 --workers=5 app.wsgi
