# -*- coding: UTF-8 -*-
import requests
from decimal import Decimal
from django.utils import timezone
from django.core.management import call_command
from diary.rules import last_trading_day
from datetime import date, timedelta, datetime


def update_stocks_prices(stocks, verbose=0):
    """
    (批量)更新股票价格
    """
    url = update_stocks_prices_url(stocks)
    content = ''
    error = 0
    while not content and error < 5:
        try:
            content = requests.get(url, timeout=3).content
        except requests.exceptions.ConnectTimeout:
            error += 1
            if verbose:
                print('retry')

    lines = content.splitlines()
    for i, line in enumerate(lines):
        try:
            stock = stocks[i]
            if verbose:
                print(line, stock, i)
            price = line.split('~')[3]
            if Decimal(price) > 0:
                stock.comment = line.decode('gb2312')
                stock.update_price(price)
        except Exception as e:
            if verbose:
                print(e)
    return True


def update_stocks_prices_url(stocks):
    """取得更新股票价格的url"""
    base_url = 'http://qt.gtimg.cn/q='
    key = []
    for stock in stocks:
        key.append('s_{}{}'.format(stock.market, stock.code))
    key = ','.join(key)
    url = base_url + key
    return url


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ('年', 60 * 60 * 24 * 365),
        ('个月', 60 * 60 * 24 * 30),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            strings.append("%s%s" % (period_value, period_name))

    return "".join(strings)


def trigger_snapshot():
    """When time is right, automatically take a snapshot of public account. """
    from stocks.models import Account
    now = datetime.now()
    if last_trading_day(now):
        if now.hour > 15:
            first_day_of_month = date(now.year, now.month, 1)
            public_account = Account.objects.get(slug='public')
            if not public_account.snapshots.filter(date__gt=first_day_of_month):
                call_command('get_price')
                public_account.take_snapshot()
