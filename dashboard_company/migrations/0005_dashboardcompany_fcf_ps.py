# Generated by Django 3.1.5 on 2021-04-27 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard_company", "0004_dashboardcompany_total_equity"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardcompany",
            name="fcf_ps",
            field=models.FloatField(default=-9999),
            preserve_default=False,
        ),
    ]