# Generated by Django 4.0.7 on 2022-09-06 20:01

import colorfield.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0019_alter_application_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromotionalCode',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('usages', models.IntegerField()),
                ('background_color', colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=18, samples=None)),
                ('color', colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=None)),
                ('application_types', models.ManyToManyField(to='application.applicationtypeconfig')),
            ],
        ),
    ]