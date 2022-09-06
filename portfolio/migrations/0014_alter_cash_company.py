# Generated by Django 4.0.4 on 2022-09-06 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ancillary_info', '0006_remove_companies_wish_list'),
        ('portfolio', '0013_cash_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cash',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.companies'),
        ),
    ]
