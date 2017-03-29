# -*- coding: UTF-8 -*-
from django.contrib import admin

from weibo_backup.models import Tweet



class TweetAdmin(admin.ModelAdmin):
    list_display = ['published', 't_id', 't_time', 'finished', ]
    list_filter = ['finished', ]

admin.site.register(Tweet, TweetAdmin)
