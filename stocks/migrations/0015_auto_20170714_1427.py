# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-14 06:27


from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0014_snapshot_extra_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snapshot',
            name='extra_content',
            field=markdownx.models.MarkdownxField(blank=True, default=b'', verbose_name='\u66f4\u591a\u5185\u5bb9'),
        ),
    ]
