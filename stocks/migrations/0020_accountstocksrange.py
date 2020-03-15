# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2020-03-15 04:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0019_auto_20180717_1236'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountStocksRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('low', models.DecimalField(blank=True, decimal_places=2, default=b'20', max_digits=5, null=True)),
                ('high', models.DecimalField(blank=True, decimal_places=2, default=b'20', max_digits=5, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.Account')),
                ('stocks', models.ManyToManyField(to='stocks.Stock')),
            ],
        ),
    ]
