# Generated by Django 4.0.4 on 2022-06-11 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ancillary_info", "0001_initial"),
        ("calculated_stats", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DcfVariables",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.CharField(max_length=255, null=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.companies",
                    ),
                ),
                (
                    "parameter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.params",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "DCF Variables",
                "db_table": "dcf_variables",
            },
        ),
    ]
