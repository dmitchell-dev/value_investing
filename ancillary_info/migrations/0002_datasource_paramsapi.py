# Generated by Django 4.0.4 on 2022-05-18 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ancillary_info', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Datasource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Datasources',
                'db_table': 'datasource',
            },
        ),
        migrations.CreateModel(
            name='ParamsApi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('param_name_api', models.CharField(max_length=255)),
                ('datasource_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.datasource')),
                ('param_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ancillary_info.params')),
            ],
            options={
                'verbose_name_plural': 'API Parameters',
                'db_table': 'params_api',
            },
        ),
    ]
