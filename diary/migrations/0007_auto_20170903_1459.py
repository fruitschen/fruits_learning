# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-03 06:59


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0006_auto_20170827_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
