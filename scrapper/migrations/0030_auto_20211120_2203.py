# Generated by Django 3.2.4 on 2021-11-20 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0029_productpagesscrapper_batchname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpagesscrapper',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='productpagesscrapper',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='variationsettings',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='variationsettings',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
    ]
