# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-20 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Weekday',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('1', '\u661f\u671f\u4e00'), ('2', '\u661f\u671f\u4e8c'), ('3', '\u661f\u671f\u4e09'), ('4', '\u661f\u671f\u56db'), ('5', '\u661f\u671f\u4e94'), ('6', '\u661f\u671f\u516d'), ('0', '\u661f\u671f\u65e5')], max_length=1, unique=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='WeekdayEventTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=128, verbose_name='\u4e8b\u4ef6')),
                ('is_task', models.BooleanField(default=False, verbose_name='\u662f\u5426\u662f\u4efb\u52a1')),
                ('priority', models.IntegerField(default=100)),
                ('start_hour', models.CharField(blank=True, choices=[(b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10'), (b'11', b'11'), (b'12', b'12'), (b'13', b'13'), (b'14', b'14'), (b'15', b'15'), (b'16', b'16'), (b'17', b'17'), (b'18', b'18'), (b'19', b'19'), (b'20', b'20'), (b'21', b'21'), (b'22', b'22'), (b'23', b'23'), (b'24', b'24')], max_length=2)),
                ('start_min', models.CharField(blank=True, choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10'), (b'11', b'11'), (b'12', b'12'), (b'13', b'13'), (b'14', b'14'), (b'15', b'15'), (b'16', b'16'), (b'17', b'17'), (b'18', b'18'), (b'19', b'19'), (b'20', b'20'), (b'21', b'21'), (b'22', b'22'), (b'23', b'23'), (b'24', b'24'), (b'25', b'25'), (b'26', b'26'), (b'27', b'27'), (b'28', b'28'), (b'29', b'29'), (b'30', b'30'), (b'31', b'31'), (b'32', b'32'), (b'33', b'33'), (b'34', b'34'), (b'35', b'35'), (b'36', b'36'), (b'37', b'37'), (b'38', b'38'), (b'39', b'39'), (b'40', b'40'), (b'41', b'41'), (b'42', b'42'), (b'43', b'43'), (b'44', b'44'), (b'45', b'45'), (b'46', b'46'), (b'47', b'47'), (b'48', b'48'), (b'49', b'49'), (b'50', b'50'), (b'51', b'51'), (b'52', b'52'), (b'53', b'53'), (b'54', b'54'), (b'55', b'55'), (b'56', b'56'), (b'57', b'57'), (b'58', b'58'), (b'59', b'59')], max_length=2)),
                ('end_hour', models.CharField(blank=True, choices=[(b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10'), (b'11', b'11'), (b'12', b'12'), (b'13', b'13'), (b'14', b'14'), (b'15', b'15'), (b'16', b'16'), (b'17', b'17'), (b'18', b'18'), (b'19', b'19'), (b'20', b'20'), (b'21', b'21'), (b'22', b'22'), (b'23', b'23'), (b'24', b'24')], max_length=2)),
                ('end_min', models.CharField(blank=True, choices=[(b'0', b'0'), (b'1', b'1'), (b'2', b'2'), (b'3', b'3'), (b'4', b'4'), (b'5', b'5'), (b'6', b'6'), (b'7', b'7'), (b'8', b'8'), (b'9', b'9'), (b'10', b'10'), (b'11', b'11'), (b'12', b'12'), (b'13', b'13'), (b'14', b'14'), (b'15', b'15'), (b'16', b'16'), (b'17', b'17'), (b'18', b'18'), (b'19', b'19'), (b'20', b'20'), (b'21', b'21'), (b'22', b'22'), (b'23', b'23'), (b'24', b'24'), (b'25', b'25'), (b'26', b'26'), (b'27', b'27'), (b'28', b'28'), (b'29', b'29'), (b'30', b'30'), (b'31', b'31'), (b'32', b'32'), (b'33', b'33'), (b'34', b'34'), (b'35', b'35'), (b'36', b'36'), (b'37', b'37'), (b'38', b'38'), (b'39', b'39'), (b'40', b'40'), (b'41', b'41'), (b'42', b'42'), (b'43', b'43'), (b'44', b'44'), (b'45', b'45'), (b'46', b'46'), (b'47', b'47'), (b'48', b'48'), (b'49', b'49'), (b'50', b'50'), (b'51', b'51'), (b'52', b'52'), (b'53', b'53'), (b'54', b'54'), (b'55', b'55'), (b'56', b'56'), (b'57', b'57'), (b'58', b'58'), (b'59', b'59')], max_length=2)),
                ('memo', models.TextField(blank=True)),
                ('weekdays', models.ManyToManyField(to='diary.Weekday')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]