# Generated by Django 4.0.4 on 2022-09-16 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0031_portfolio_income_from_selling_portfolio_total_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='latest_financial_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='latest_share_price_date',
            field=models.DateTimeField(null=True),
        ),
    ]