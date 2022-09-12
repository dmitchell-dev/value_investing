# Generated by Django 4.0.4 on 2022-09-12 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0030_portfolio_sold_shares_income'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='income_from_selling',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='portfolio',
            name='total_profit',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
