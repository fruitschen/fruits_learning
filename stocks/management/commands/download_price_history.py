# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from stocks.models import Stock

class Command(BaseCommand):
    help = u'下载股票历史价格'

    def handle(self, *args, **options):
        stocks = Stock.objects.filter(tracking=True)
        i = 0
        count = stocks.count()
        if options.get('verbosity'):
            print 'Updating {} stocks. '.format(count)
        for stock in stocks:
            stock.download_price_history()

