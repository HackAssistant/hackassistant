# Generated by Django 4.0.10 on 2023-06-07 12:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0008_commentreaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentreaction',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]