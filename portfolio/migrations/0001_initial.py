# Generated by Django 4.0.4 on 2022-08-01 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("ancillary_info", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WishList",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reporting_stock_price", models.FloatField()),
                ("current_stock_price", models.FloatField()),
                ("reporting_mos", models.FloatField()),
                ("current_mos", models.FloatField()),
                ("buy_mos", models.FloatField()),
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
                    "decision",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.decisiontype",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Wish List",
                "db_table": "wish_list",
            },
        ),
        migrations.CreateModel(
            name="Portfolio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("num_shares", models.IntegerField()),
                ("current_stock_price", models.FloatField()),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.companies",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Portfolio",
                "db_table": "portfolio",
            },
        ),
        migrations.CreateModel(
            name="Investments",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_dealt", models.DateField()),
                ("date_settled", models.DateField()),
                ("reference", models.CharField(max_length=255)),
                ("num_stock", models.IntegerField()),
                ("price", models.FloatField()),
                ("fees", models.FloatField()),
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
                    "decision",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ancillary_info.decisiontype",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Investments",
                "db_table": "investments",
            },
        ),
    ]
