# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-26 05:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0014_diary_events_generated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='events_generated',
            field=models.BooleanField(default=False),
        ),
    ]
