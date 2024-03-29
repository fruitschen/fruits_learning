# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2020-04-25 16:24


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('info_collector', '0014_author_following'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='names', to='info_collector.Author')),
            ],
        ),
    ]
