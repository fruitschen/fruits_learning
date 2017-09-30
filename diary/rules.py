from datetime import timedelta


def first_20_days(the_date):
    return the_date.day <= 20


def not_first_20_days(the_date):
    return not first_20_days(the_date)


def last_trading_day(the_date):
    new_date = the_date
    trading_day = the_date
    mon_to_fri = [0, 1, 2, 3, 4]
    if the_date.weekday() not in mon_to_fri:
        return False
    while new_date.month == the_date.month:
        if new_date.weekday() in mon_to_fri:  # Mon through Fri
            trading_day = new_date
        new_date = new_date + timedelta(days=1)
    return trading_day == the_date


def last_sunday(the_date):
    if the_date.weekday() != 6:
        return False
    new_date = the_date
    the_last_sunday = the_date
    while new_date.month == the_date.month:
        if new_date.weekday() == 6:  # Sunday
            the_last_sunday = new_date
        new_date = new_date + timedelta(days=1)
    return the_last_sunday == the_date


rules = [
    'first_20_days',
    'not_first_20_days',
    'last_trading_day',
    'last_sunday',
]


RULES_CHOICES = zip(rules, rules)
