# Generated by Django 4.0.4 on 2022-08-12 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_applicationlog_date_alter_applicationlog_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationtypeconfig',
            name='auto_confirm',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='applicationtypeconfig',
            name='needs_confirmation',
            field=models.BooleanField(default=False),
        ),
    ]
