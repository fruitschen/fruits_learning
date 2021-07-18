# -*- coding: UTF-8 -*-


from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save
from django.template.loader import render_to_string

from django.urls import reverse

import os
from datetime import date, timedelta
from PIL import Image as PILImage
from PIL import ExifTags

from diary.rules import RULES_CHOICES
import diary.rules

DATE_FORMAT = '%Y-%m-%d'


class Diary(models.Model):
    date = models.DateField()
    events_generated = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    @property
    def max_content_order(self):
        if not self.contents.exists():
            return 0
        else:
            return self.contents.order_by('-order')[0].order

    @property
    def formatted_date(self):
        return self.date.strftime(DATE_FORMAT)

    @property
    def weekday(self):
        return WEEKDAY_DICT[str(self.date.weekday())]

    def get_absolute_url(self):
        return reverse('diary_details', args=[self.formatted_date])

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Diaries'


def get_diary_media_path(instance, filename):
    diary = instance.diary
    path = os.path.join('diary', str(diary.date.year), str(diary.date.month), filename)
    return path


class DiaryContent(models.Model):
    diary = models.ForeignKey('Diary', related_name='contents', on_delete=models.CASCADE)
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

    @property
    def as_dict(self):
        content_obj = getattr(self, self.content_attr)
        return content_obj.as_dict

    class Meta:
        ordering = ['order']


class DiaryText(DiaryContent):
    text = models.TextField()

    def render(self):
        return render_to_string('diary/include/content_text.html', {'content': self, })

    @property
    def as_dict(self):
        return {
            'title': self.title,
            'content': self.text,
            'type': 'text',
        }


class DiaryImage(DiaryContent):
    image = models.ImageField(upload_to=get_diary_media_path)

    def render(self):
        return render_to_string('diary/include/content_image.html', {'content': self, 'MEDIA_URL': settings.MEDIA_URL })

    @property
    def as_dict(self):
        return {
            'title': self.title,
            'content': self.image.url,
            'type': 'image',
        }


class DiaryAudio(DiaryContent):
    audio = models.FileField(upload_to=get_diary_media_path)

    def render(self):
        return render_to_string('diary/include/content_audio.html', {'content': self, 'MEDIA_URL': settings.MEDIA_URL })

    @property
    def as_dict(self):
        return {
            'title': self.title,
            'content': self.audio.url,
            'type': 'audio',
        }


class EventGroup(models.Model):
    name = models.CharField(max_length=64, )
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', ]

    def __unicode__(self):
        return self.name


HOURS = [str(i) for i in range(1, 25)]
MINS = [str(i) for i in range(60)]
HOUR_CHOICES = list(zip(HOURS, HOURS))
MIN_CHOICES = list(zip(MINS, MINS))


class BaseEventTemplate(models.Model):
    group = models.ForeignKey(EventGroup, null=True, blank=True, on_delete=models.CASCADE)
    event = models.CharField('事件', max_length=128)
    is_task = models.BooleanField('是否是任务', default=False)
    priority = models.IntegerField(default=100)
    start_hour = models.CharField(max_length=2, choices=HOUR_CHOICES, blank=True)
    start_min = models.CharField(max_length=2, choices=MIN_CHOICES, blank=True)
    end_hour = models.CharField(max_length=2, choices=HOUR_CHOICES, blank=True)
    end_min = models.CharField(max_length=2, choices=MIN_CHOICES, blank=True)
    memo = models.TextField(blank=True)
    tags = models.CharField(max_length=128, default='', blank=True)
    mandatory = models.BooleanField(
        '必须完成?', default=False, help_text='过去未完成的mandatory任务会继续显示在今日任务里。'
    )
    events = GenericRelation('Event')

    link_title = models.CharField(max_length=128, blank=True)
    link_url = models.CharField(max_length=512, blank=True)
    is_archived = models.BooleanField(default=False)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

    @property
    def tags_list(self):
        if not self.tags:
            return []
        return self.tags.split(',')

    def to_event(self, event_date, commit=False):
        event = Event(
            group=self.group,
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
            tags=self.tags,
            mandatory=self.mandatory,
            link_title=self.link_title,
            link_url=self.link_url,
        )
        if commit:
            event.event_template = self
            event.save()
        return event


WEEKDAY_CHOICES = (
    ('0', '星期一'),
    ('1', '星期二'),
    ('2', '星期三'),
    ('3', '星期四'),
    ('4', '星期五'),
    ('5', '星期六'),
    ('6', '星期日'),
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
    weekdays = models.ManyToManyField('Weekday', blank=True)

    def __unicode__(self):
        return '{} {} (Weekday Event Template)'.format(self.event, '、'.join(
            [w.get_weekday_display() for w in self.weekdays.all()])
        )

    def get_admin_url(self):
        return reverse('admin:diary_weekdayeventtemplate_change', args=(self.id, ))


DAYS = [str(i) for i in range(1, 32)]
DAY_CHOICES = list(zip(DAYS, DAYS))


class MonthEventTemplate(BaseEventTemplate):
    event_type = 'month_event'
    day = models.CharField('日', max_length=2, choices=DAY_CHOICES)  # 31日表示最后一天

    def __unicode__(self):
        return '{} {}日 (Month Event Template)'.format(self.event, self.day)

    def get_admin_url(self):
        return reverse('admin:diary_montheventtemplate_change', args=(self.id,))


MONTHS = [str(i) for i in range(1, 13)]
MONTH_CHOICES = list(zip(MONTHS, MONTHS))


class AnnualEventTemplate(BaseEventTemplate):
    event_type = 'annual_event'
    month = models.CharField('月', max_length=2, choices=MONTH_CHOICES)
    day = models.CharField('日', max_length=2, choices=DAY_CHOICES)

    def __unicode__(self):
        return '{} {}月{}日 (Annual Event Template)'.format(self.event, self.month, self.day)

    def get_admin_url(self):
        return reverse('admin:diary_annualeventtemplate_change', args=(self.id,))


class RuleEventTemplate(BaseEventTemplate):
    event_type = 'rule_event'
    rule = models.CharField(max_length=64, choices=RULES_CHOICES)
    generate_event = models.BooleanField(default=False)

    @property
    def is_done(self):
        # just a dummy property
        return False

    def applicable_to_date(self, the_date):
        func = getattr(diary.rules, self.rule)
        return func(the_date)

    def to_event(self, event_date, commit=False):
        if self.generate_event:
            query = Event.objects.filter(event_date=event_date, event_type=self.event_type, event=self.event)
            if query:
                return query[0]
            return super(RuleEventTemplate, self).to_event(event_date=event_date, commit=commit)
        else:
            return self

    def get_admin_url(self):
        return reverse('admin:diary_ruleeventtemplate_change', args=(self.id,))

    def __unicode__(self):
        return '{}'.format(self.event)

    @property
    def event_template(self):
        return self


class Event(BaseEventTemplate):
    event_date = models.DateField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    done_timestamp = models.DateTimeField(default=None, null=True, blank=True)
    event_type = models.CharField(max_length=64)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    event_template = GenericForeignKey('content_type', 'object_id')

    is_deleted = models.BooleanField(default=False)
    is_event_instance = True

    def to_event(self):
        return self

    def __unicode__(self):
        event = '{}'.format(self.event)
        if self.start_hour:
            event += ' {}:{}'.format(self.start_hour, self.start_min or 0)
        return event

    @property
    def is_delayed_mandatory(self):
        if not self.mandatory or not self.event_date:
            return False
        today = date.today()
        return not self.is_done and self.event_date < today

    @property
    def formatted_date(self):
        return self.event_date.strftime(DATE_FORMAT)

    @property
    def finish_rate(self):
        if not self.event_template:
            return None
        today = date.today()
        start = today - timedelta(days=30)
        events = self.event_template.events.all().filter(event_date__gte=start, is_deleted=False)
        total = events.count()
        finished = events.filter(is_done=True).count()
        return {
            'total': total,
            'finished': finished,
            'finish_rate': finished / total,
            'finish_rate_text': '{}/{}'.format(finished, total),
        }



def generate_weekdays(**kwargs):
    days = list(range(0, 7))
    for weekday in days:
        Weekday.objects.get_or_create(weekday=weekday)

post_migrate.connect(generate_weekdays, sender=Weekday._meta.app_config)


AUTO_EVENT_TYPES = [
    MonthEventTemplate.event_type,
    WeekdayEventTemplate.event_type,
    RuleEventTemplate.event_type,
]
EVENT_TYPES = AUTO_EVENT_TYPES + [
    'manual',
]


class Exercise(models.Model):
    name = models.CharField('事件', max_length=128)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']


class ExerciseLog(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    times = models.IntegerField(default=0)
    date = models.DateField()

    @property
    def range(self):
        return list(range(self.times))


def generate_exercises(**kwargs):
    default_exercises = [
        '平板支撑',
        '平躺抬腿',
        '深蹲',
        '跳绳100',
    ]
    for ex in default_exercises:
        Exercise.objects.get_or_create(name=ex)

post_migrate.connect(generate_exercises, sender=Exercise._meta.app_config)


for orientation in list(ExifTags.TAGS.keys()):
    if ExifTags.TAGS[orientation] == 'Orientation':
        break


def resize_image(path):
    max_width = 1080
    img = PILImage.open(path)
    if hasattr(img, '_getexif'):
        # we need to rotate the image based on exif info.
        # https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
        exif = img._getexif()
        if not exif:
            return
        exif = dict(list(img._getexif().items()))
        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)
    original_width, original_height = img.size
    if original_width < max_width:  # no need to resize
        return
    width_percent = (max_width / float(original_width))
    new_height = int((float(original_height) * float(width_percent)))
    img = img.resize((max_width, new_height), PILImage.ANTIALIAS)
    img.save(path)


def image_post_save(sender, instance, **kwargs):
    image_path = instance.image.path
    if os.path.exists(image_path):
        resize_image(image_path)

post_save.connect(image_post_save, sender=DiaryImage)
