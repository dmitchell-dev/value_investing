# Generated by Django 4.0.4 on 2022-09-02 19:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ancillary_info', '0006_remove_companies_wish_list'),
        ('portfolio', '0008_remove_portfolio_id_alter_portfolio_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cash',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_dealt', models.DateField()),
                ('cash_value', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('decision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.decisiontype')),
            ],
            options={
                'verbose_name_plural': 'Cash',
                'db_table': 'cash',
            },
        ),
    ]
