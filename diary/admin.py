from django.contrib import admin

from diary.models import *


class WeekdayEventTemplateAdmin(admin.ModelAdmin):
    model = WeekdayEventTemplate
    filter_horizontal = ['weekdays']


class MonthEventTemplateAdmin(admin.ModelAdmin):
    model = MonthEventTemplate


class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display = ['event', 'event_date', 'is_task', 'is_done']
    list_filter = ['is_task']

admin.site.register(WeekdayEventTemplate, WeekdayEventTemplateAdmin)
admin.site.register(MonthEventTemplate, MonthEventTemplateAdmin)
admin.site.register(Event, EventAdmin)

