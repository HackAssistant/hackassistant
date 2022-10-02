# Generated by Django 4.0.4 on 2022-09-01 09:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('application', '0015_edition_application_edition'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='application',
            unique_together={('type', 'user', 'edition')},
        ),
    ]
