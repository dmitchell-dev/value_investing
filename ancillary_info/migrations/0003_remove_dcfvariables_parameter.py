# Generated by Django 4.0.4 on 2022-08-01 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ancillary_info', '0002_alter_companies_wish_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dcfvariables',
            name='parameter',
        ),
    ]
