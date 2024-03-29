# Generated by Django 4.0.7 on 2022-09-06 10:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('application', '0018_remove_applicationtypeconfig_group_and_more'),
        ('review', '0004_delete_blockedlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=100)),
                ('accept', models.BooleanField()),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.application')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('can_review_file', 'Can review file'),),
            },
        ),
    ]
