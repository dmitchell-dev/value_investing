# Generated by Django 4.0.4 on 2022-09-10 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0019_positionperformance_portfolio_cash_holding'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='PositionPerformance',
        ),
    ]
