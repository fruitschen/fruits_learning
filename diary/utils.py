from diary.models import WeekdayEventTemplate, Weekday, MonthEventTemplate, Event
from datetime import timedelta


def get_events_by_date(the_date, commit=False):
    events_query = Event.objects.filter(event_date=the_date)
    if events_query:
        return events_query
    weekday = Weekday.objects.get(weekday=str(the_date.weekday()))
    weekday_event_templates = weekday.weekdayeventtemplate_set.all()

    month_event_templates = MonthEventTemplate.objects.filter(day=the_date.day)
    event_templates = list(weekday_event_templates) + list(month_event_templates)
    events = []
    for tpl in event_templates:
        events.append(tpl.to_event(the_date, commit=commit))
    return events


def is_end_of_month(the_date):
    current_month = the_date.month
    if (the_date + timedelta(days=1)).momth != current_month:
        return True
    else:
        return False
