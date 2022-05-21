# Generated by Django 4.0.4 on 2022-05-18 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CompanyType",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Company Types",
                "db_table": "company_type",
            },
        ),
        migrations.CreateModel(
            name="Countries",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Countries",
                "db_table": "countries",
            },
        ),
        migrations.CreateModel(
            name="Currencies",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Currencies",
                "db_table": "currencies",
            },
        ),
        migrations.CreateModel(
            name="Exchanges",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Exchanges",
                "db_table": "exchanges",
            },
        ),
        migrations.CreateModel(
            name="Industries",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Industries",
                "db_table": "industries",
            },
        ),
        migrations.CreateModel(
            name="ReportType",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Report Types",
                "db_table": "report_type",
            },
        ),
        migrations.CreateModel(
            name="Sectors",
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
                ("value", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Sectors",
                "db_table": "sectors",
            },
        ),
        migrations.CreateModel(
            name="Params",
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
                ("param_name", models.CharField(max_length=255)),
                ("param_name_col", models.CharField(max_length=255)),
                ("limit_logic", models.CharField(max_length=255)),
                ("limit_value", models.CharField(max_length=255)),
                ("data_type", models.CharField(max_length=255)),
                ("param_description", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "report_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.reporttype",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Parameters",
                "db_table": "params",
            },
        ),
        migrations.CreateModel(
            name="Companies",
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
                ("tidm", models.CharField(max_length=10)),
                ("company_name", models.CharField(max_length=255)),
                ("company_summary", models.TextField()),
                (
                    "comp_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.companytype",
                    ),
                ),
                (
                    "exchange",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.exchanges",
                    ),
                ),
                (
                    "industry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.industries",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Companies",
                "db_table": "companies",
            },
        ),
    ]
