# Generated by Django 4.0.4 on 2022-08-01 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
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
                ("wish_list", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Companies",
                "db_table": "companies",
            },
        ),
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
            name="CompSource",
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
                "verbose_name_plural": "Company Sources",
                "db_table": "comp_sources",
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
            name="Datasource",
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
                ("source_name", models.CharField(max_length=255)),
            ],
            options={
                "verbose_name_plural": "Datasources",
                "db_table": "datasources",
            },
        ),
        migrations.CreateModel(
            name="DecisionType",
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
                "verbose_name_plural": "Decision Types",
                "db_table": "decision_type",
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
                ("param_description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Parameters",
                "db_table": "params",
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
            name="ParamsApi",
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
                ("param_name_api", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "datasource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.datasource",
                    ),
                ),
                (
                    "param",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.params",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "API Parameters",
                "db_table": "params_api",
            },
        ),
        migrations.AddField(
            model_name="params",
            name="report_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.reporttype",
            ),
        ),
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
                ("est_growth_rate", models.FloatField()),
                ("est_disc_rate", models.FloatField()),
                ("est_ltg_rate", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
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
        migrations.AddField(
            model_name="companies",
            name="comp_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.companytype",
            ),
        ),
        migrations.AddField(
            model_name="companies",
            name="company_source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.compsource",
            ),
        ),
        migrations.AddField(
            model_name="companies",
            name="country",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.countries",
            ),
        ),
        migrations.AddField(
            model_name="companies",
            name="currency",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.currencies",
            ),
        ),
        migrations.AddField(
            model_name="companies",
            name="exchange",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.exchanges",
            ),
        ),
        migrations.AddField(
            model_name="companies",
            name="industry",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="ancillary_info.industries",
            ),
        ),
        migrations.AddField(
            model_name="companies",
            name="sector",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ancillary_info.sectors"
            ),
        ),
    ]
