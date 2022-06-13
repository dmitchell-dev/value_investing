# Generated by Django 4.0.4 on 2022-06-13 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_company', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dashboardcompany',
            old_name='earnings_yield_return',
            new_name='annual_yield_return',
        ),
        migrations.AddField(
            model_name='dashboardcompany',
            name='earnings_yield',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]
