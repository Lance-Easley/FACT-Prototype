# Generated by Django 3.1.7 on 2021-03-08 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0003_contract_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contract',
            old_name='date',
            new_name='datetime',
        ),
    ]
