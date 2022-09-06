# Generated by Django 4.0.7 on 2022-09-06 20:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0021_application_promotional_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='promotionalcode',
            name='application_types',
        ),
        migrations.AlterField(
            model_name='promotionalcode',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='Use this code to the apply url as ?promotional_code=[uuid]', primary_key=True, serialize=False),
        ),
    ]
