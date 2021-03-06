# Generated by Django 3.1.5 on 2021-02-04 21:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ancillary_info", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="calcvariables",
            options={"verbose_name_plural": "Calculation Variables"},
        ),
        migrations.AlterModelOptions(
            name="companies",
            options={"verbose_name_plural": "Companies"},
        ),
        migrations.AlterModelOptions(
            name="companytype",
            options={"verbose_name_plural": "Company Types"},
        ),
        migrations.AlterModelOptions(
            name="industries",
            options={"verbose_name_plural": "Industries"},
        ),
        migrations.AlterModelOptions(
            name="industryrisk",
            options={"verbose_name_plural": "Industry Risks"},
        ),
        migrations.AlterModelOptions(
            name="markets",
            options={"verbose_name_plural": "Markets"},
        ),
        migrations.AlterModelOptions(
            name="parameters",
            options={"verbose_name_plural": "Parameters"},
        ),
        migrations.AlterModelOptions(
            name="reportsection",
            options={"verbose_name_plural": "Report Sections"},
        ),
        migrations.AlterModelOptions(
            name="reporttype",
            options={"verbose_name_plural": "Report Types"},
        ),
    ]
