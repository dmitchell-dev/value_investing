# Generated by Django 3.1.5 on 2021-02-10 19:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ancillary_info', '0002_auto_20210204_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='RankingStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateField()),
                ('value', models.CharField(max_length=255, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.companies')),
                ('parameter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.parameters')),
            ],
            options={
                'verbose_name_plural': 'Ranking Stats',
                'db_table': 'ranking_data',
            },
        ),
    ]
