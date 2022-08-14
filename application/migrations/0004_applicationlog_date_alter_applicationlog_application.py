# Generated by Django 4.0.4 on 2022-08-10 10:24

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0003_alter_application_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationlog',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='applicationlog',
            name='application',
            field=models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='application.application'),
        ),
    ]