# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand

from stocks.models import Stock, StockPair
from stocks.utils import update_stocks_prices

class Command(BaseCommand):
    help = u'更新股票价格'

    def add_arguments(self, parser):
        parser.add_argument('--all',
            action='store_true',
            dest='all',
            default=False,
            help=u'更新全部股票')

    def handle(self, *args, **options):
        stocks = Stock.objects.exclude(archive=True)
        if options.get('all'):
            stocks = Stock.objects.all()
            pairs = StockPair.objects.all()
        else:
            stocks = stocks.filter(star=True)
            pairs = StockPair.objects.filter(star=True)

        i = 0
        while i < stocks.count():
            group = stocks[i:i+50]
            update_stocks_prices(group)
            i += 50

        if options.get('verbose'):
            print 'Done'
        for pair in pairs:
            pair.update_if_needed()
        if options.get('verbose'):
            print 'Updated Pairs'
