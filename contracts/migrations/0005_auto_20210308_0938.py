# Generated by Django 3.1.7 on 2021-03-08 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0004_auto_20210308_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contract',
            name='datetime',
        ),
        migrations.AlterField(
            model_name='contract',
            name='contract_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
