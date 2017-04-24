# -*- coding: UTF-8 -*-
from django.contrib import admin

from reads.models import Read


class ReadAdmin(admin.ModelAdmin):
    search_fields = ['title', ]


admin.site.register(Read, ReadAdmin)
