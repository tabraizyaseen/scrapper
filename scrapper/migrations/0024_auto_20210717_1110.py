# Generated by Django 3.2.4 on 2021-07-17 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0023_auto_20210707_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='variationsettings',
            name='old_price',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='variationsettings',
            name='price',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
