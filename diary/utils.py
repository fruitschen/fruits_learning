from diary.models import WeekdayEventTemplate, Weekday, MonthEventTemplate, Event, RuleEventTemplate
from datetime import timedelta


def get_events_by_date(the_date, commit=False):
    events_query = Event.objects.filter(event_date=the_date).order_by('priority')

    rule_events = []
    rule_event_templates = RuleEventTemplate.objects.all()
    for tpl in rule_event_templates:
        if tpl.applicable_to_date(the_date):
            rule_events.append(tpl.to_event(the_date, commit=commit))

    if events_query:
        return list(events_query) + rule_events

    weekday = Weekday.objects.get(weekday=str(the_date.weekday()))
    weekday_event_templates = weekday.weekdayeventtemplate_set.all()

    month_event_templates = MonthEventTemplate.objects.filter(day=the_date.day)
    event_templates = list(weekday_event_templates) + list(month_event_templates)
    event_templates = sorted(event_templates, key=lambda x:x.priority)
    events = []
    for tpl in event_templates:
        events.append(tpl.to_event(the_date, commit=commit))

    events.extend(rule_events)

    return events


def is_end_of_month(the_date):
    current_month = the_date.month
    if (the_date + timedelta(days=1)).momth != current_month:
        return True
    else:
        return False
