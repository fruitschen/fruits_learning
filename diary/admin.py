from django.contrib import admin

from diary.models import *


class WeekdayEventTemplateAdmin(admin.ModelAdmin):
    model = WeekdayEventTemplate
    filter_horizontal = ['weekdays']
    list_display = ['event', 'is_task', 'priority', 'tags',]
    list_filter = ['is_task', 'weekdays', ]
    list_editable = ['tags', ]

class MonthEventTemplateAdmin(admin.ModelAdmin):
    model = MonthEventTemplate
    list_editable = ['tags', ]
    list_display = ['event', 'day', 'is_task', 'priority', 'tags', ]
    list_filter = ['is_task', 'day', ]


class RuleEventTemplateAdmin(admin.ModelAdmin):
    model = RuleEventTemplate
    list_editable = ['tags', ]
    list_display = ['event', 'is_task', 'generate_event', 'priority', 'tags', 'rule']
    list_filter = ['is_task', 'generate_event', ]


class EventAdmin(admin.ModelAdmin):
    model = Event
    list_editable = ['tags', ]
    list_display = ['event', 'event_date', 'is_task', 'is_done', 'tags']
    list_filter = ['is_task', 'is_done', 'event_date', 'event_type', ]


admin.site.register(WeekdayEventTemplate, WeekdayEventTemplateAdmin)
admin.site.register(MonthEventTemplate, MonthEventTemplateAdmin)
admin.site.register(RuleEventTemplate, RuleEventTemplateAdmin)
admin.site.register(Event, EventAdmin)
