# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-25 15:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0010_auto_20170915_1035'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('order', models.PositiveIntegerField(default=1)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='event',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='diary.EventGroup'),
        ),
        migrations.AddField(
            model_name='montheventtemplate',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='diary.EventGroup'),
        ),
        migrations.AddField(
            model_name='ruleeventtemplate',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='diary.EventGroup'),
        ),
        migrations.AddField(
            model_name='weekdayeventtemplate',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='diary.EventGroup'),
        ),
    ]