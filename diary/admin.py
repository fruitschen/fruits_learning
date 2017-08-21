from django.contrib import admin

from diary.models import *


class WeekdayEventTemplateAdmin(admin.ModelAdmin):
    model = WeekdayEventTemplate
    filter_horizontal = ['weekdays']

admin.site.register(WeekdayEventTemplate, WeekdayEventTemplateAdmin)
