# Generated by Django 4.0.4 on 2022-08-28 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_remove_wishlist_id_alter_wishlist_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investments',
            name='decision',
        ),
    ]
