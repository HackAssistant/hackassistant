# Generated by Django 4.0.7 on 2022-09-06 21:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0023_alter_application_promotional_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='promotional_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.promotionalcode'),
        ),
    ]
