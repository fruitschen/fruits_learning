# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2020-04-25 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_collector', '0013_info_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='following',
            field=models.BooleanField(default=False),
        ),
    ]