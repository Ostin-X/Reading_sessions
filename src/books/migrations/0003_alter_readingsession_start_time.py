# Generated by Django 4.2.7 on 2023-11-20 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_readingsession_total_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readingsession',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
