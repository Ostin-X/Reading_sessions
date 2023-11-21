# Generated by Django 4.2.7 on 2023-11-21 19:24

import books.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_readingprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readingprofile',
            name='daily_reading_time',
            field=models.JSONField(default=books.models.get_empty_list),
        ),
    ]
