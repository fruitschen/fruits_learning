# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-12 15:24


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_collector', '0005_info_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='starred',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='info',
            name='starred_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
