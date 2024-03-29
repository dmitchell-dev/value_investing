# Generated by Django 4.0.4 on 2022-09-11 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0028_rename_pct_holding_portfolio_company_pct_holding'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='fees_bought',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='fees_sold',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='fees_total',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='initial_shares_cost',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='initial_shares_holding',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='latest_share_price',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='share_pct_change',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='share_value_change',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
