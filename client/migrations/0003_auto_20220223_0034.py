# Generated by Django 2.2 on 2022-02-23 00:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0002_sale'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='user',
            new_name='user_id',
        ),
    ]
