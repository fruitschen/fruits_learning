# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.signals import post_migrate
from django.template.loader import render_to_string


class Diary(models.Model):
    date = models.DateField()

    @property
    def max_content_order(self):
        if not self.contents.exists():
            return 0
        else:
            return self.contents.order_by('-order')[0].order


class DiaryContent(models.Model):
    diary = models.ForeignKey('Diary', related_name='contents')
    order = models.IntegerField(null=True)
    title = models.CharField(blank=True, max_length=128)
    content_attr = models.CharField(max_length=20)

    def save(self, **kwargs):
        if not self.order:
            self.order = self.diary.max_content_order + 1
        super(DiaryContent, self).save(**kwargs)

    def render(self):
        content_obj = getattr(self, self.content_attr)
        return content_obj.render()

    class Meta:
        ordering = ['order']


class DiaryText(DiaryContent):
    text = models.TextField()

    def render(self):
        return render_to_string('diary/include/content_text.html', {'content': self, })


class DiaryImage(DiaryContent):
    image = models.ImageField(upload_to='diary')

    def render(self):
        return render_to_string('diary/include/content_image.html', {'content': self, 'MEDIA_URL': settings.MEDIA_URL })


HOURS = [str(i) for i in range(1, 25)]
MINS = [str(i) for i in range(60)]
HOUR_CHOICES = zip(HOURS, HOURS)
MIN_CHOICES = zip(MINS, MINS)


class BaseEventTemplate(models.Model):
    event = models.CharField(u'事件', max_length=128)
    is_task = models.BooleanField(u'是否是任务', default=False)
    priority = models.IntegerField(default=100)
    start_hour = models.CharField(max_length=2, choices=HOUR_CHOICES, blank=True)
    start_min = models.CharField(max_length=2, choices=MIN_CHOICES, blank=True)
    end_hour = models.CharField(max_length=2, choices=HOUR_CHOICES, blank=True)
    end_min = models.CharField(max_length=2, choices=MIN_CHOICES, blank=True)
    memo = models.TextField(blank=True)

    class Meta:
        abstract = True


WEEKDAY_CHOICES = (
    ('0', u'星期一'),
    ('1', u'星期二'),
    ('2', u'星期三'),
    ('3', u'星期四'),
    ('4', u'星期五'),
    ('5', u'星期六'),
    ('6', u'星期日'),
)


class Weekday(models.Model):
    event_type = 'weekday_event'
    weekday = models.CharField(choices=WEEKDAY_CHOICES, unique=True, max_length=1)

    def __unicode__(self):
        return self.get_weekday_display()

    class Meta:
        ordering = ['weekday']


class WeekdayEventTemplate(BaseEventTemplate):
    weekdays = models.ManyToManyField('Weekday')

    def __unicode__(self):
        return '{} (Weekday Event Template)'.format(self.event, )

u'''
TODO:
class MonthEventTemplate(BaseEventTemplate):
    event_type = 'month_event'
    day = models.CharField('日', max_length=2)  # 31日表示最后一天

is_end_of_month

'''


def generate_weekdays(**kwargs):
    days = range(0, 7)
    for weekday in days:
        Weekday.objects.get_or_create(weekday=weekday)

post_migrate.connect(generate_weekdays, sender=Weekday._meta.app_config)
