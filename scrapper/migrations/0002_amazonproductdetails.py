# Generated by Django 3.1.5 on 2021-02-22 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='amazonProductDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productID', models.CharField(blank=True, max_length=20, null=True)),
                ('attributes', models.CharField(blank=True, max_length=200, null=True)),
                ('values', models.CharField(blank=True, max_length=512, null=True)),
            ],
        ),
    ]
