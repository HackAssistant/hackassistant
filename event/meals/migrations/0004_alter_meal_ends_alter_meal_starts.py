# Generated by Django 4.0.8 on 2023-03-13 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0003_alter_meal_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='ends',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='meal',
            name='starts',
            field=models.DateTimeField(),
        ),
    ]
