# -*- coding: UTF-8 -*-
import os
import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from stocks.models import Stock, StockPair
from stocks.utils import update_stocks_prices


class Command(BaseCommand):
    help = u'更新股票价格，默认只更新收藏的股票'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--all',
            action='store_true',
            dest='all',
            default=False,
            help=u'更新全部股票'
        )

    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        pairs = StockPair.objects.filter(star=True)
        print 'Updating'
        # 1. Try local update files first.
        update_file_path = '/home/fruitschen/Downloads/'
        files = os.listdir(update_file_path)
        stocks_files = filter(lambda f: f.startswith('stocks_update') and f.endswith('.json'), files)
        if stocks_files:
            last_file = stocks_files[-1]
            file_path = os.path.join(update_file_path, last_file)
            content = open(file_path, 'r').read()
            stocks_info = json.loads(content)
            for key, info in stocks_info.items():
                code = info['code'][-6:]
                price = info['price']
                if price == '--':
                    continue
                if Stock.objects.filter(code=code).exists():
                    stock = Stock.objects.get(code=code)
                    stock.update_price(Decimal(price))
            for f in stocks_files:
                file_path = os.path.join(update_file_path, f)
                os.unlink(file_path)
            print 'Done. '
        else:
            # 2. No local update info available. Let's go get them.
            if options.get('all'):
                stocks = Stock.objects.all()
                pairs = StockPair.objects.all()
                print 'All Stocks'
            else:
                stocks = stocks.filter(star=True)
                pairs = StockPair.objects.filter(star=True)
                print 'Used Stocks'
    
            i = 0
            count = stocks.count()
            while i < count:
                group = stocks[i:i+50]
                update_stocks_prices(group)
                i += 50

            if options.get('verbosity'):
                print 'Done updating {} stocks. '.format(count)
        for pair in pairs:
            pair.update_if_needed()
        if options.get('verbosity'):
            print 'Updated Pairs'
