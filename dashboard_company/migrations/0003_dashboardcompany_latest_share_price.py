# Generated by Django 4.0.4 on 2022-09-03 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_company', '0002_alter_dashboardcompany_annual_yield_return_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardcompany',
            name='latest_share_price',
            field=models.FloatField(null=True),
        ),
    ]
