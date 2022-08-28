# Generated by Django 4.0.4 on 2022-08-28 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ancillary_info', '0006_remove_companies_wish_list'),
        ('portfolio', '0004_remove_investments_decision'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wishlist',
            name='decision',
        ),
        migrations.AddField(
            model_name='investments',
            name='decision',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.decisiontype'),
            preserve_default=False,
        ),
    ]
