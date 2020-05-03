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
    silence = models.BooleanField(default=False)

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
    following = models.BooleanField(default=False)
    stop_fetching = models.BooleanField(u'停止抓取', default=False)
    last_fetched = models.DateTimeField(null=True, blank=True)
    last_day_count = models.IntegerField(default=0)
    last_week_count = models.IntegerField(default=0)
    last_month_count = models.IntegerField(default=0)
    last_year_count = models.IntegerField(default=0)
    raw = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.name or u'[no name]'

    def natural_key(self):
        return (self.user_id, self.name)

    @property
    def should_fetch(self):
        """
        total = 0
        for author in Author.objects.filter(following=True):
            if author.should_fetch:
                total += 1
        print(total)
        """
        now = timezone.now()
        if self.stop_fetching:
            return False
        if not self.last_fetched:
            return True
        since_last_fetched = now - self.last_fetched
        # never again within an hour
        if since_last_fetched < timedelta(minutes=60):
            return False
        # not within a week if there are fewer than 20 items last month
        if self.last_month_count < 20 and since_last_fetched < timedelta(days=7):
            return False
        # not within a day if there are fewer than 20 items last week
        if self.last_week_count < 20 and since_last_fetched < timedelta(days=1):
            return False
        # not within 3 hours if there are fewer than 10 items last day
        if self.last_day_count < 10 and since_last_fetched < timedelta(minutes=60*3):
            return False
        return True

    def update_aggregate(self):
        info_set = self.info_set.all()
        now = timezone.now()
        self.last_day_count = info_set.filter(timestamp__gt=now-timedelta(days=1)).count()
        self.last_week_count = info_set.filter(timestamp__gt=now - timedelta(days=7)).count()
        self.last_month_count = info_set.filter(timestamp__gt=now - timedelta(days=30)).count()
        self.last_year_count = info_set.filter(timestamp__gt=now - timedelta(days=365)).count()
        last_info_query = info_set.order_by('-timestamp')
        if last_info_query:
            last_info = last_info_query[0]
            if not self.last_fetched or last_info.timestamp > self.last_fetched:
                self.last_fetched = last_info.timestamp
        self.save()
        
    def save_name(self):
        if not self.names.filter(name=self.name).exists():
            AuthorName.objects.create(author=self, name=self.name)
            return True
        

class AuthorName(models.Model):
    author = models.ForeignKey(Author, related_name='names')
    name = models.CharField(max_length=128, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.name
    

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
    tags = models.CharField(max_length=256, blank=True)
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
    important = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    length = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        unique_together = (('info_source', 'identifier'),)
        ordering = ['-important', '-timestamp']

    def __unicode__(self):
        return self.title or ''

    def natural_key(self):
        return (self.info_source.id, self.identifier)

    def delete_me(self):
        self.is_deleted = True
        self.save()

    @property
    def safe_content(self):
        if self.content:
            return self.content.content
        else:
            return ''

    @property
    def create_read_url(self):
        return '{}?info={}'.format(reverse('admin:reads_read_add'), self.id)

    def save(self, **kwargs):
        if not self.length and self.content:
            self.length = len(self.content.content)
        super(Info, self).save(**kwargs)


class Content(models.Model):
    content = models.TextField(blank=True)


class SyncLog(models.Model):
    action = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '{} {}'.format(self.action, self.timestamp)

    class Meta:
        ordering = ['-id']
