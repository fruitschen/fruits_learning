# coding: utf-8
from __future__ import unicode_literals
from datetime import timedelta
from django.utils import timezone
from django.db import models


class InfoSource(models.Model):
    GOOD = 'G'
    ERROR = 'E'
    CRAWLING = 'C'
    CURRENT_STATUS = (
        (GOOD, u'✓ good'),
        (ERROR, u'× error'),
        (CRAWLING, u'~ running')
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    url = models.URLField()
    last_fetched = models.DateTimeField(null=True, blank=True)
    last_error = models.DateTimeField(null=True, blank=True)
    interval = models.IntegerField(u'抓取间隔(秒)', default=15*60)
    status = models.CharField(max_length=1, default=GOOD, choices=CURRENT_STATUS)
    description = models.TextField()

    class Meta:
        ordering = ('name',)

    def should_fetch(self):
        if not self.last_fetched:
            return True
        now = timezone.now()
        return self.last_fetched + timedelta(seconds=self.interval) < now

    def __unicode__(self):
        return self.name


class Info(models.Model):
    NEW = 'N'
    OK = 'O'
    ERROR = 'E'
    STATUS = (
        (NEW, 'New'),
        (OK, 'Ok'),
        (ERROR, 'Error'),
    )

    info_source = models.ForeignKey(InfoSource, related_name='stories')
    title = models.CharField(max_length=500, null=True, blank=True)
    identifier = models.CharField(max_length=255)
    url = models.URLField(max_length=2000, null=True, blank=True)
    content = models.OneToOneField('Content', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    original_timestamp = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, default=NEW, choices=STATUS)

    class Meta:
        unique_together = (('info_source', 'identifier'),)
        ordering = ('-timestamp',)

    def __unicode__(self):
        return self.title


class Content(models.Model):
    content = models.TextField(blank=True)

