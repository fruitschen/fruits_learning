# coding: utf-8


from django.db import models


class Read(models.Model):
    slug = models.SlugField(unique=True, db_index=True)
    info = models.ForeignKey('info_collector.Info', limit_choices_to={'starred': True, }, null=True, blank=True)
    title = models.CharField('标题', max_length=128, blank=True)
    original_url = models.CharField('原文URL', max_length=128, blank=True)
    home = models.BooleanField('是否显示在主页', default=True)
    note = models.TextField('笔记', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # timeliness = models.ForeignKey()  # TODO #

    def __unicode__(self):
        return self.title or self.info.title

    def get_title(self):
        if self.title:
            return self.title
        elif self.info:
            return self.info.title

    def get_original_url(self):
        if self.original_url:
            return self.original_url
        elif self.info:
            return self.info.url
