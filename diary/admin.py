from django.contrib import admin

from diary.models import *


class WeekdayEventTemplateAdmin(admin.ModelAdmin):
    model = WeekdayEventTemplate
    filter_horizontal = ['weekdays']
    list_display = ['event', 'is_task', 'priority', ]
    list_filter = ['is_task', 'weekdays', ]


class MonthEventTemplateAdmin(admin.ModelAdmin):
    model = MonthEventTemplate
    list_display = ['event', 'day', 'is_task', 'priority', ]
    list_filter = ['is_task', 'day', ]


class RuleEventTemplateAdmin(admin.ModelAdmin):
    model = RuleEventTemplate
    list_display = ['event', 'is_task', 'generate_event', 'priority', 'rule']
    list_filter = ['is_task', 'generate_event', ]


class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display = ['event', 'event_date', 'is_task', 'is_done']
    list_filter = ['is_task', 'is_done', 'event_date', 'event_type', ]


admin.site.register(WeekdayEventTemplate, WeekdayEventTemplateAdmin)
admin.site.register(MonthEventTemplate, MonthEventTemplateAdmin)
admin.site.register(RuleEventTemplate, RuleEventTemplateAdmin)
admin.site.register(Event, EventAdmin)
