# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 06:36


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_collector', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='status',
            field=models.CharField(choices=[('N', 'New'), ('O', 'Ok'), ('E', 'Error')], default='N', max_length=1),
        ),
    ]
