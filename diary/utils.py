from diary.models import WeekdayEventTemplate, Weekday


def get_events_by_date(the_date):
    print the_date
    print the_date.weekday()
    weekday = Weekday.objects.get(weekday=str(the_date.weekday()))
    print weekday
    event_templates = weekday.weekdayeventtemplate_set.all()
    return event_templates

