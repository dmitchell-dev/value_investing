# Generated by Django 4.0.4 on 2022-09-12 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0029_portfolio_fees_bought_portfolio_fees_sold_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='sold_shares_income',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
