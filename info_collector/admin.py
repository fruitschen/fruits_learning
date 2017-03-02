# -*- coding: UTF-8 -*-
from django.contrib import admin

from info_collector.models import InfoSource, Info


class InfoSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status', 'last_fetched', 'last_error', 'interval', ]


class InfoAdmin(admin.ModelAdmin):
    list_filter = ['info_source', ]

admin.site.register(InfoSource, InfoSourceAdmin)
admin.site.register(Info, InfoAdmin)
