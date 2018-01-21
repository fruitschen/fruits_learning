# -*- coding: UTF-8 -*-
from diary.models import Diary, WeekdayEventTemplate, Weekday, MonthEventTemplate, Event, RuleEventTemplate, \
    AUTO_EVENT_TYPES, AnnualEventTemplate
from datetime import timedelta, date


def get_events_by_date(diary, tag='', commit=False, include_deleted=False):
    the_date = diary.date
    events_query = Event.objects.filter(event_date=the_date).order_by('priority')
    if not include_deleted:
        events_query = events_query.filter(is_deleted=False)
    # This is explicit now.
    events_generated = diary.events_generated

    rule_events_tpls = []
    rule_event_templates = RuleEventTemplate.objects.all()
    for tpl in rule_event_templates:
        if not tpl.generate_event and tpl.applicable_to_date(the_date):
            rule_events_tpls.append(tpl)

    if events_generated:
        events = list(events_query) + rule_events_tpls
    else:
        weekday = Weekday.objects.get(weekday=str(the_date.weekday()))
        weekday_event_templates = weekday.weekdayeventtemplate_set.all()

        month_event_templates = MonthEventTemplate.objects.filter(day=the_date.day)

        annual_event_templates = AnnualEventTemplate.objects.filter(month=the_date.month, day=the_date.day)

        event_templates = list(weekday_event_templates) + list(month_event_templates) + list(annual_event_templates)

        for tpl in rule_event_templates:
            if tpl.generate_event and tpl.applicable_to_date(the_date):
                event_templates.append(tpl)

        events = list(events_query)
        for tpl in event_templates:
            events.append(tpl.to_event(the_date, commit=commit))
        if commit:
            diary.events_generated = True
            diary.save()
        events.extend(rule_events_tpls)

    today = date.today()
    if today == the_date:
        # only show unfinished_mandatory_events for today.
        unfinished_mandatory_events = Event.objects.filter(mandatory=True, is_done=False, event_date__lt=today)
        if not include_deleted:
            unfinished_mandatory_events = unfinished_mandatory_events.filter(is_deleted=False)
        events += unfinished_mandatory_events
    events = sorted(events, key=lambda x: x.priority)

    if tag:
        events = filter(lambda x: tag in x.tags, events)
    return events


def is_end_of_month(the_date):
    current_month = the_date.month
    if (the_date + timedelta(days=1)).momth != current_month:
        return True
    else:
        return False


def age_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        (u'岁', 60 * 60 * 24 * 365),
        (u'个月', 60 * 60 * 24 * 30),
        (u'天', 60 * 60 * 24),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            strings.append("%s%s" % (period_value, period_name))

    return "".join(strings)