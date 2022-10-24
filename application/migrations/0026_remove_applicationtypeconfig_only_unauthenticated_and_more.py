# Generated by Django 4.0.7 on 2022-10-07 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0025_remove_applicationtypeconfig_public_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicationtypeconfig',
            name='only_unauthenticated',
        ),
        migrations.AddField(
            model_name='applicationtypeconfig',
            name='only_authenticated',
            field=models.BooleanField(default=False, help_text='Setting this to True, user will need to be authenticated tp apply'),
        ),
        migrations.AlterField(
            model_name='applicationtypeconfig',
            name='create_user',
            field=models.BooleanField(default=True, help_text='Setting this to True creates a user if it was not authenticated create a user for him to enter later'),
        ),
    ]