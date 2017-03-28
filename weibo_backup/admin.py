# -*- coding: UTF-8 -*-
from django.contrib import admin

from weibo_backup.models import Tweet



class TweetAdmin(admin.ModelAdmin):
    list_display = ['t_id', 'finished',  ]

admin.site.register(Tweet, TweetAdmin)
