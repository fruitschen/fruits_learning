# -*- coding: UTF-8 -*-
from django.contrib import admin

from info_collector.models import InfoSource, Info, Author, SyncLog


class InfoSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'last_fetched', 'last_error', 'interval', ]


class InfoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'info_source', 'timestamp', 'original_timestamp']
    list_filter = ['info_source', 'is_read', 'important']


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = [
        'name', 'url', 'following', 'stop_fetching', 'last_fetched', 'last_day_count', 'last_week_count',
        'last_month_count', 'last_year_count',
    ]
    list_filter = ['following', ]


class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'action', 'timestamp']


admin.site.register(InfoSource, InfoSourceAdmin)
admin.site.register(Info, InfoAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(SyncLog, SyncLogAdmin)
