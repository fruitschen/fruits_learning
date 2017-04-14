# -*- coding: UTF-8 -*-
from django.contrib import admin

from info_collector.models import InfoSource, Info, Author


class InfoSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'last_fetched', 'last_error', 'interval', ]


class InfoAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'info_source', 'timestamp', 'original_timestamp']
    list_filter = ['info_source', 'is_read', ]

class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']

admin.site.register(InfoSource, InfoSourceAdmin)
admin.site.register(Info, InfoAdmin)
admin.site.register(Author, AuthorAdmin)
