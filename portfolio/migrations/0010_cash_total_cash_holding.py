# Generated by Django 4.0.4 on 2022-09-03 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0009_cash'),
    ]

    operations = [
        migrations.AddField(
            model_name='cash',
            name='total_cash_holding',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
