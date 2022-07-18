# Generated by Django 4.0.4 on 2022-07-04 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ancillary_info", "0003_paramsapi_created_at_paramsapi_updated_at"),
        ("dashboard_company", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="dashboardcompany",
            name="company",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.companies",
            ),
            preserve_default=False,
        ),
    ]