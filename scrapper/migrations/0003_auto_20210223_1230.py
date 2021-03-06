# Generated by Django 3.1.5 on 2021-02-23 07:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0002_amazonproductdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amazonproductdetails',
            name='productID',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='scrapper.amazonproductpagesscrapper'),
        ),
        migrations.CreateModel(
            name='productImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.CharField(blank=True, max_length=512, null=True)),
                ('productID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='scrapper.amazonproductpagesscrapper')),
            ],
        ),
    ]
