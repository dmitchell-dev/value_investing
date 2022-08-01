# Generated by Django 4.0.4 on 2022-08-01 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ancillary_info', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareSplits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateField()),
                ('value', models.FloatField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.companies')),
            ],
            options={
                'verbose_name_plural': 'Share Splits',
                'db_table': 'share_split',
            },
        ),
        migrations.CreateModel(
            name='SharePrices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateField()),
                ('value', models.FloatField(null=True)),
                ('value_adjusted', models.FloatField(null=True)),
                ('volume', models.BigIntegerField(null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.companies')),
            ],
            options={
                'verbose_name_plural': 'Share Prices',
                'db_table': 'share_price',
            },
        ),
    ]
