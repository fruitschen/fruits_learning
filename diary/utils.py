from diary.models import WeekdayEventTemplate, Weekday, MonthEventTemplate, Event, RuleEventTemplate, AUTO_EVENT_TYPES
from datetime import timedelta


def get_events_by_date(the_date, commit=False):
    events_query = Event.objects.filter(event_date=the_date).order_by('priority')
    # TODO: This should be explicit
    events_generated = events_query.filter(event_type__in=AUTO_EVENT_TYPES).exists()

    rule_events_tpls = []
    rule_event_templates = RuleEventTemplate.objects.all()
    for tpl in rule_event_templates:
        if not tpl.generate_event and tpl.applicable_to_date(the_date):
            rule_events_tpls.append(tpl)

    if events_generated:
        return list(events_query) + rule_events_tpls

    weekday = Weekday.objects.get(weekday=str(the_date.weekday()))
    weekday_event_templates = weekday.weekdayeventtemplate_set.all()

    month_event_templates = MonthEventTemplate.objects.filter(day=the_date.day)
    event_templates = list(weekday_event_templates) + list(month_event_templates)

    for tpl in rule_event_templates:
        if tpl.generate_event and tpl.applicable_to_date(the_date):
            event_templates.append(tpl)

    events = list(events_query)
    for tpl in event_templates:
        events.append(tpl.to_event(the_date, commit=commit))

    events.extend(rule_events_tpls)
    events = sorted(events, key=lambda x:x.priority)

    return events


def is_end_of_month(the_date):
    current_month = the_date.month
    if (the_date + timedelta(days=1)).momth != current_month:
        return True
    else:
        return False
