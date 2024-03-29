# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 05:54


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('identifier', models.CharField(max_length=255)),
                ('url', models.URLField(blank=True, max_length=2000, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('original_timestamp', models.DateTimeField(null=True)),
                ('content', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='info_collector.Content')),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='InfoSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('url', models.URLField()),
                ('last_fetched', models.DateTimeField(blank=True, null=True)),
                ('last_error', models.DateTimeField(blank=True, null=True)),
                ('interval', models.IntegerField(default=900, verbose_name='\u6293\u53d6\u95f4\u9694')),
                ('status', models.CharField(choices=[('G', '\u2713 good'), ('E', '\xd7 error'), ('C', '~ running')], default='G', max_length=1)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='info',
            name='info_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stories', to='info_collector.InfoSource'),
        ),
        migrations.AlterUniqueTogether(
            name='info',
            unique_together=set([('info_source', 'identifier')]),
        ),
    ]
