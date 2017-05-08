# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.utils.html import strip_tags

from reads.models import Read
from info_collector.models import Info


class ReadAdmin(admin.ModelAdmin):
    search_fields = ['title', ]

    def get_changeform_initial_data(self, request):
        initial = super(ReadAdmin, self).get_changeform_initial_data(request)
        if 'info' in initial:
            info = Info.objects.get(id=initial['info'])
            initial['slug'] = 'info-{}-{}'.format(info.original_timestamp.strftime('%Y-%m-%d'), info.id)
            initial['title'] = info.title
            initial['original_url'] = info.url
            if info.content:
                initial['note'] = strip_tags(
                    info.content.content.replace('<p>', '\n').replace('<br>', '\n').replace('<br />', '\n')
                )
        return initial


admin.site.register(Read, ReadAdmin)
