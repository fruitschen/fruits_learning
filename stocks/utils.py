# -*- coding: UTF-8 -*-
import os
import json
import urllib2
import requests
from datetime import datetime
from decimal import Decimal

from django.utils import timezone

def update_stocks_prices(stocks, verbose=0):
    url = update_stocks_prices_url(stocks)
    content = ''
    error = 0
    while not content and error < 5:
        try:
            content = requests.get(url, timeout=3).content
        except requests.exceptions.ConnectTimeout:
            error += 1
            if verbose:
                print 'retry'

    lines = content.splitlines()
    for i, line in enumerate(lines):
        try:
            stock = stocks[i]
            if verbose:
                print line, stock, i
            price = line.split('~')[3]
            if Decimal(price) > 0:
                stock.price = price
                stock.price_updated = timezone.now()
                stock.save()
        except Exception, e:
            if verbose:
                print e
    return True


def update_stocks_prices_url(stocks):
    base_url = 'http://qt.gtimg.cn/q='
    key = []
    for stock in stocks:
        key.append('s_{}{}'.format(stock.market, stock.code))
    key = ','.join(key)
    url = base_url + key
    return url

