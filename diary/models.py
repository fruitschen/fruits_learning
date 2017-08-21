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

    def to_event(self, event_date, commit=False):
        event = Event(
            event=self.event,
            is_task=self.is_task,
            priority=self.priority,
            start_hour=self.start_hour,
            start_min=self.start_min,
            end_hour=self.end_hour,
            end_min=self.end_min,
            memo=self.memo,
            event_date=event_date,
            event_type=self.event_type,
        )
        if commit:
            event.save()
        return event


WEEKDAY_CHOICES = (
    ('0', u'星期一'),
    ('1', u'星期二'),
    ('2', u'星期三'),
    ('3', u'星期四'),
    ('4', u'星期五'),
    ('5', u'星期六'),
    ('6', u'星期日'),
)
WEEKDAY_DICT = dict(WEEKDAY_CHOICES)


class Weekday(models.Model):
    weekday = models.CharField(choices=WEEKDAY_CHOICES, unique=True, max_length=1)

    def __unicode__(self):
        return self.get_weekday_display()

    class Meta:
        ordering = ['weekday']


class WeekdayEventTemplate(BaseEventTemplate):
    event_type = 'weekday_event'
    weekdays = models.ManyToManyField('Weekday')

    def __unicode__(self):
        return '{} {} (Weekday Event Template)'.format(self.event, u'、'.join([w.get_weekday_display() for w in self.weekdays.all()]))


DAYS = [str(i) for i in range(1, 32)]
DAY_CHOICES = zip(DAYS, DAYS)


class MonthEventTemplate(BaseEventTemplate):
    event_type = 'month_event'
    day = models.CharField('日', max_length=2, choices=DAY_CHOICES)  # 31日表示最后一天

    def __unicode__(self):
        return u'{} {}日 (Month Event Template)'.format(self.event, self.day)


class Event(BaseEventTemplate):
    event_date = models.DateField()
    is_done = models.BooleanField(default=False)
    event_type = models.CharField(max_length=64)

    def to_event(self):
        return self

    def __unicode__(self):
        event = '{}'.format(self.event)
        if self.start_hour:
            event += ' {}:{}'.format(self.start_hour, self.start_min or 0)
        return event


def generate_weekdays(**kwargs):
    days = range(0, 7)
    for weekday in days:
        Weekday.objects.get_or_create(weekday=weekday)

post_migrate.connect(generate_weekdays, sender=Weekday._meta.app_config)
