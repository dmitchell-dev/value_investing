# Generated by Django 3.1.5 on 2021-02-08 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('share_prices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shareprices',
            name='adjustment',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='shareprices',
            name='value',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='shareprices',
            name='volume',
            field=models.IntegerField(),
        ),
    ]
