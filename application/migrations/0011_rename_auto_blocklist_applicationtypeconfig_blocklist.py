# Generated by Django 4.0.4 on 2022-08-23 18:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0010_remove_applicationtypeconfig_needs_confirmation_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationtypeconfig',
            old_name='auto_blocklist',
            new_name='blocklist',
        ),
    ]