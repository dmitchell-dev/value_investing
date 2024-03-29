# Generated by Django 4.0.4 on 2022-09-10 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ancillary_info', '0006_remove_companies_wish_list'),
        ('portfolio', '0018_remove_portfolio_cash_holding'),
    ]

    operations = [
        migrations.CreateModel(
            name='PositionPerformance',
            fields=[
                ('month_end_date', models.DateField()),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='ancillary_info.companies')),
                ('num_shares_bought', models.IntegerField()),
                ('price_paid', models.IntegerField()),
                ('num_shares_sold', models.IntegerField()),
                ('price_earned', models.IntegerField()),
                ('fees_paid', models.FloatField()),
                ('current_stock_price', models.FloatField()),
            ],
            options={
                'verbose_name_plural': 'Position Performance',
                'db_table': 'position_performance',
            },
        ),
        migrations.AddField(
            model_name='portfolio',
            name='cash_holding',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
