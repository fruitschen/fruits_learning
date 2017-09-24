from __future__ import unicode_literals

import os
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'tweets')


# Create your models here.
class Tweet(models.Model):
    t_id = models.CharField(max_length=64, blank=True, db_index=True)
    t_time = models.CharField(max_length=64, blank=True)
    published = models.DateTimeField(default=None, null=True, blank=True)
    finished = models.BooleanField(default=False)
    content = models.TextField(default='')

    def status_url(self):
        return 'http://m.weibo.cn/status/{}'.format(self.t_id)

    @property
    def media_dir(self):
        if self.t_id:
            media_dir = os.path.join(BASE_DIR, self.t_id[:4])
        else:
            media_dir = os.path.join(BASE_DIR, 'unknown')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
        return media_dir

    @property
    def screenshot_full(self):
        return os.path.join(self.media_dir, '{}_full.png'.format(self.id))

    @property
    def screenshot_full_url(self):
        return self.screenshot_full.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)

    @property
    def screenshot_pictures(self):
        return os.path.join(self.media_dir, '{}_pics.png'.format(self.id))

    def save(self, *args, **kwargs):
        if self.t_time and not self.published:
            if not self.t_time[:4].isdigit():
                now = timezone.now()
                self.t_time = '{}-{}'.format(now.year, self.t_time)
            try:
                published = datetime.strptime(self.t_time, '%Y-%m-%d %H:%M')
            except ValueError:
                published = datetime.strptime(self.t_time, '%Y-%m-%d')
            self.published = timezone.datetime(published.year, published.month, published.day, published.hour,
                                               published.minute, tzinfo=timezone.get_current_timezone())

        super(Tweet, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-published']