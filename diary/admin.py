from django.contrib import admin

from diary.models import *


class EventGroupAdmin(admin.ModelAdmin):
    model = EventGroup


class WeekdayEventTemplateAdmin(admin.ModelAdmin):
    model = WeekdayEventTemplate
    filter_horizontal = ['weekdays']
    list_display = ['event', 'is_task', 'priority', 'tags', 'group']
    list_filter = ['is_task', 'weekdays', ]
    list_editable = ['tags', 'group', ]


class MonthEventTemplateAdmin(admin.ModelAdmin):
    model = MonthEventTemplate
    list_editable = ['tags', 'group', ]
    list_display = ['event', 'day', 'is_task', 'priority', 'tags', 'group']
    list_filter = ['is_task', 'day', ]


class AnnualEventTemplateAdmin(admin.ModelAdmin):
    model = AnnualEventTemplate
    list_editable = ['tags', 'group', ]
    list_display = ['event', 'month', 'day', 'is_task', 'priority', 'tags', 'group']
    list_filter = ['is_task', 'day', ]


class RuleEventTemplateAdmin(admin.ModelAdmin):
    model = RuleEventTemplate
    list_editable = ['tags', 'group', ]
    list_display = ['event', 'is_task', 'generate_event', 'priority', 'tags', 'group', 'rule']
    list_filter = ['is_task', 'generate_event', ]


class EventAdmin(admin.ModelAdmin):
    model = Event
    list_editable = ['tags', 'group', ]
    list_display = ['event', 'event_date', 'is_task', 'is_done', 'tags', 'group']
    list_filter = ['is_task', 'is_done', 'event_date', 'event_type', 'is_deleted']


class DiaryAdmin(admin.ModelAdmin):
    model = Diary
    list_display = ['date', 'events_generated']
    list_filter = ['date', 'events_generated']

admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(WeekdayEventTemplate, WeekdayEventTemplateAdmin)
admin.site.register(MonthEventTemplate, MonthEventTemplateAdmin)
admin.site.register(AnnualEventTemplate, AnnualEventTemplateAdmin)
admin.site.register(RuleEventTemplate, RuleEventTemplateAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Diary, DiaryAdmin)
