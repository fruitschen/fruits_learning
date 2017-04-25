# coding: utf-8
from __future__ import unicode_literals
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.core.urlresolvers import reverse


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


class AuthorManager(models.Manager):
    def get_by_natural_key(self, user_id, name):
        return self.get(user_id=user_id, name=name)


class Author(models.Model):
    objects = AuthorManager()

    user_id = models.CharField(max_length=256, blank=True)
    name = models.CharField(max_length=128, blank=True)
    url = models.CharField(max_length=1000, blank=True)
    avatar_url = models.CharField(max_length=1000, blank=True)
    raw = models.TextField(blank=True)

    def __unicode__(self):
        return self.name or u'[no name]'

    def natural_key(self):
        return (self.user_id, self.name)


class InfoManager(models.Manager):
    def get_by_natural_key(self, info_source, identifier):
        return self.get(info_source=info_source, identifier=identifier)


class Info(models.Model):
    NEW = 'N'
    OK = 'O'
    ERROR = 'E'
    STATUS = (
        (NEW, 'New'),
        (OK, 'Ok'),
        (ERROR, 'Error'),
    )
    objects = InfoManager()

    info_source = models.ForeignKey(InfoSource, related_name='stories')
    title = models.CharField(max_length=500, null=True, blank=True)
    author = models.ForeignKey('Author', null=True, blank=True, on_delete=models.SET_NULL)
    identifier = models.CharField(max_length=255)
    url = models.URLField(max_length=2000, null=True, blank=True)
    content = models.OneToOneField('Content', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    original_timestamp = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, default=NEW, choices=STATUS)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    starred_at = models.DateTimeField(null=True, blank=True)
    starred = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        unique_together = (('info_source', 'identifier'),)
        ordering = ('-timestamp',)

    def __unicode__(self):
        return self.title or ''

    def natural_key(self):
        return (self.info_source.id, self.identifier)

    def delete_me(self):
        self.is_deleted = True
        self.save()

    @property
    def create_read_url(self):
        return '{}?info={}'.format(reverse('admin:reads_read_add'), self.id)


class Content(models.Model):
    content = models.TextField(blank=True)
