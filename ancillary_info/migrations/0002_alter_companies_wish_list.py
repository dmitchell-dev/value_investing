# Generated by Django 4.0.4 on 2022-08-01 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ancillary_info", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="companies",
            name="wish_list",
            field=models.CharField(max_length=5),
        ),
    ]
