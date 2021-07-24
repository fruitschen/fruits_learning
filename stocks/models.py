# -*- coding: UTF-8 -*-
"""
券商有时候给出四舍五入的均价，自动计算交易额的时候，可能造成成交额有一点误差。
"""
from __future__ import unicode_literals
import os
from decimal import Decimal
from datetime import timedelta, datetime
from django.utils import timezone

from django.urls import reverse
from django.conf import settings
from django.db import models
from django.db.models import Q, Sum

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from stocks.utils import td_format


'''
分红处理代码
from decimal import Decimal
stock = Stock.objects.get(code='600340')
trans = PairTransaction.objects.filter(finished__isnull=True, bought_stock=stock)
for transaction in trans:
    transaction.bought_price -= Decimal('0.5')
    transaction.save()

sold_trans = PairTransaction.objects.filter(finished__isnull=True, sold_stock=stock)
for transaction in sold_trans:
    transaction.sold_price -= Decimal('0.5')
    transaction.save()


bs_trans = BoughtSoldTransaction.objects.filter(finished__isnull=True, bought_stock=stock)
for b in bs_trans:
    b.bought_price -= Decimal('0.5')
    b.save()


trans = PairTransaction.objects.filter(finished__isnull=True, bought_stock=stock)
for transaction in trans:
    transaction.bought_price /= Decimal('2.2')
    transaction.bought_amount *= Decimal('2.2')
    transaction.save()


sold_trans = PairTransaction.objects.filter(finished__isnull=True, sold_stock=stock)
for transaction in sold_trans:
    transaction.sold_price /= Decimal('2.2')
    transaction.sold_amount *= Decimal('2.2')
    transaction.save()
    

'''


def ratio_display(ratio):
    if ratio < 0.2:
        ratio = ratio.quantize(Decimal('0.0000'))
    else:
        ratio = ratio.quantize(Decimal('0.000'))
    return ratio


class Transaction(models.Model):
    """一笔买入、卖出交易"""
    BUY = '买入'
    SELL = '卖出'
    ACTION_CHOICES = (
        (BUY, BUY),
        (SELL, SELL),
    )
    account = models.ForeignKey('Account', blank=True, null=True, on_delete=models.PROTECT, related_name='transactions')
    action = models.CharField('交易类型', max_length=16, blank=True, choices=ACTION_CHOICES)
    stock = models.ForeignKey(
        'Stock', verbose_name='股票', limit_choices_to={'star': True},
        related_name='transactions', on_delete=models.PROTECT
    )
    price = models.DecimalField('交易价格', max_digits=10, decimal_places=4, null=True, blank=True)
    amount = models.IntegerField('交易数量',)
    date = models.DateTimeField('交易时间', null=True, blank=True)
    total_money = models.DecimalField('交易额', max_digits=20, decimal_places=4, null=True, blank=True)
    has_updated_account = models.BooleanField('是否已经更新账户', default=False)

    def save(self, *args, **kwargs):
        """如果没有填交易额，在save之前自动计算。"""
        if not self.total_money:
            self.total_money = self.price * self.amount
        if not self.has_updated_account:
            self.update_account()
        super(Transaction, self).save(*args, **kwargs)

    def update_account(self):
        """只更新股票，不更新现金和负债。"""
        if self.has_updated_account:
            return
        account_stock_query = self.account.stocks.filter(stock=self.stock)
        if self.action == Transaction.BUY:
            if account_stock_query.exists():
                account_stock = account_stock_query[0]
                account_stock.amount += self.amount
                account_stock.save()
            else:
                account_stock = AccountStock.objects.create(stock=self.stock, amount=self.amount, account=self.account)
        elif self.action == Transaction.SELL:
            account_stock = account_stock_query[0]
            account_stock.amount -= self.amount
            account_stock.save()
        self.has_updated_account = True


class StockPair(models.Model):
    """一组配对交易标的"""
    name = models.CharField(max_length=256, default='')
    started_stock = models.ForeignKey(
        'Stock', limit_choices_to={'star': True}, related_name='pairs', on_delete=models.PROTECT
    )
    target_stock = models.ForeignKey(
        'Stock', limit_choices_to={'star': True}, related_name='targeted_pairs', on_delete=models.PROTECT
    )
    star = models.BooleanField(default=False, blank=True)
    current_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    value_updated = models.DateTimeField(null=True, blank=True)

    order = models.IntegerField(default=100)

    class Meta:
        ordering = ['star', 'order']

    def __str__(self):
        if not self.name:
            self.name = '{}/{}'.format(self.started_stock.name, self.target_stock.name)
            self.save()
        return self.name

    @property
    def current_value_display(self):
        return ratio_display(self.current_value)

    def update(self):
        """更新配对的比值"""
        if not self.started_stock.price or not self.target_stock.price:
            return
        if not self.value_updated or \
                (self.started_stock.price_updated > self.value_updated) or \
                (self.target_stock.price_updated > self.value_updated):
            self.current_value = self.started_stock.price / self.target_stock.price
            self.value_updated = timezone.now()
            self.save()

    def update_if_needed(self):
        """如果股票的价格有变动则更新比值。"""
        if not self.value_updated or self.value_updated < (timezone.now() + timedelta(minutes=1)):
            self.update()
    
    @property
    def last_transaction(self):
        if self.unfinished_transactions:
            query = self.unfinished_transactions
        else:
            query = self.transactions.all()
        if query:
            last_transaction = query.order_by('-id')[0]
        else:
            last_transaction = None
        return last_transaction
    
    @property
    def unfinished_transactions(self):
        return self.transactions.filter(finished__isnull=True).exclude(archived=True)
    
    @property
    def recent_finished_transactions(self):
        query = self.transactions.filter(finished__isnull=False).exclude(archived=True).order_by('-id')
        return query[:2]

    
    @property
    def note(self):
        last_transaction = self.last_transaction
        if last_transaction:
            if last_transaction.finished:
                ratio = self.last_transaction.back_ratio
            else:
                ratio = self.last_transaction.to_ratio
            ratio = round(ratio * 10000) / 10000
            
            return ratio
    
    @property
    def status(self):
        """计算配对今日的涨跌幅"""
        change_one = Decimal(self.started_stock.status['price_change_percent'])
        change_two = Decimal(self.target_stock.status['price_change_percent'])
        change_percent = ((100 + change_one) / (100 + change_two) - 1) * 100
        return {
            'change_percent': change_percent
        }


class PairTransaction(models.Model):
    """一笔完整的配对交易"""
    account = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='pair_transactions')
    pair = models.ForeignKey(
        StockPair, limit_choices_to={'star': True}, null=True, blank=True,
        related_name='transactions', on_delete=models.PROTECT
    )
    sold_stock = models.ForeignKey(
        'Stock', verbose_name='卖出股票', limit_choices_to={'star': True},
        related_name='sold_pair_transactions', on_delete=models.PROTECT
    )
    sold_price = models.DecimalField('卖出价格', max_digits=10, decimal_places=4)
    sold_amount = models.IntegerField('卖出数量',)
    bought_stock = models.ForeignKey(
        'Stock', verbose_name='买入股票', limit_choices_to={'star': True},
        related_name='bought_pair_transactions', on_delete=models.PROTECT
    )
    bought_price = models.DecimalField('买入价格', max_digits=10, decimal_places=4)
    bought_amount = models.IntegerField('买入数量',)
    started = models.DateTimeField('交易时间', null=True, blank=True)
    finished = models.DateTimeField('结束交易时间', null=True, blank=True)
    sold_bought_back_price = models.DecimalField(
        '卖出后买入价格', max_digits=10, decimal_places=4, null=True, blank=True
    )
    bought_back_amount = models.IntegerField(
        '实际买回数量', null=True, blank=True,
        help_text='实际买回的数量可能和之前卖出的数量不一致，这个值用于显示Transaction的交易额，并不用于计算配对交易的利润。'
    )
    bought_sold_price = models.DecimalField('买入后卖出价格', max_digits=10, decimal_places=4, null=True, blank=True)
    profit = models.DecimalField('利润', max_digits=10, decimal_places=4, null=True, blank=True)
    order = models.IntegerField(default=100)
    archived = models.BooleanField('存档-不再计算盈亏', default=False)

    transactions = models.ManyToManyField(Transaction, editable=False)

    class Meta:
        ordering = ['order', 'finished', '-started']

    def __str__(self):
        return '{} 配对交易'.format(self.pair)

    @property
    def sold_total(self):
        return self.sold_price * self.sold_amount

    @property
    def bought_total(self):
        return self.bought_price * self.bought_amount

    @property
    def sold_bought_back_total(self):
        if self.finished:
            return self.sold_bought_back_price * self.sold_amount
        return self.sold_amount * self.sold_stock.price

    @property
    def bought_sold_total(self):
        if self.finished:
            return self.bought_sold_price * self.bought_amount
        return self.bought_amount * self.bought_stock.price

    @property
    def total(self):
        """四笔交易的总交易额"""
        total = self.sold_total + self.sold_bought_back_total + self.bought_sold_total + self.bought_total
        return total

    @property
    def total_finished(self):
        """已经发生的总交易额"""
        total = self.sold_total + self.bought_total
        if self.finished:
            total += self.sold_bought_back_total + self.bought_sold_total
        return total

    @property
    def profit_before_fee(self):
        return self.sold_total - self.sold_bought_back_total + self.bought_sold_total - self.bought_total

    @property
    def money_taken(self):
        """占用资金"""
        return max(self.bought_total, self.sold_total)

    @property
    def percent(self):
        """利润占占用资金的百分比"""
        return '%.2f%%' % (self.get_profit() / self.money_taken * 100)

    @property
    def fee(self):
        """手续费假设为千分之一"""
        return self.total * Decimal('0.001')

    def get_profit(self):
        if self.finished and self.profit:
            return self.profit
        profit = self.profit_before_fee - self.fee
        return profit

    @property
    def to_ratio(self):
        """配对，换过去交易时候的比值"""
        if self.sold_stock == self.pair.started_stock:
            ratio = self.sold_price / self.bought_price
        else:
            ratio = self.bought_price / self.sold_price
        return ratio

    @property
    def to_ratio_display(self):
        return self.ratio_display(self.to_ratio)

    @property
    def back_ratio_display(self):
        return self.ratio_display(self.back_ratio)

    def ratio_display(self, ratio):
        if ratio < 0.2:
            ratio = ratio.quantize(Decimal('0.0000'))
        else:
            ratio = ratio.quantize(Decimal('0.000'))
        return ratio

    @property
    def back_ratio(self):
        """配对换回来时候的比值"""
        if self.finished:
            if self.sold_stock == self.pair.started_stock:
                ratio = self.sold_bought_back_price / self.bought_sold_price
            else:
                ratio = self.bought_sold_price / self.sold_bought_back_price
            return ratio

    def save(self, **kwargs):
        """
        如果没有填配对，自动设置或者创建pair
        如果信息足够，计算利润。
        """
        if not self.pair:
            pair = StockPair.objects.filter(
                Q(started_stock=self.sold_stock, target_stock=self.bought_stock) |
                Q(started_stock=self.bought_stock, target_stock=self.sold_stock)
            )
            if not pair.exists():
                pair = StockPair.objects.create(started_stock=self.sold_stock, target_stock=self.bought_stock)
            else:
                pair = pair[0]
            pair.star = True
            pair.save()
            self.pair = pair

        if not self.profit and self.finished:
            self.profit = self.get_profit()
        super(PairTransaction, self).save(**kwargs)
        self.as_transactions()

    def as_transactions(self):
        """
        把配对交易以四笔Transaction交易的形式显示
        (如果没完成的话就是两笔交易)
        """
        start_transactions = [
            # sold
            Transaction(
                account=self.account,
                date=self.started, action='卖出', stock=self.sold_stock, amount=self.sold_amount,
                price=self.sold_price, total_money=self.sold_total),
            # bought
            Transaction(
                account=self.account,
                date=self.started, action='买入', stock=self.bought_stock, amount=self.bought_amount,
                price=self.bought_price, total_money=self.bought_total),
        ]
        if self.transactions.all().count() < 2:
            for t in start_transactions:
                t.save()
                self.transactions.add(t)
        end_transactions = []
        if self.finished:
            actual_bought_back_amount = self.bought_back_amount or self.sold_amount
            actual__bought_back_total = actual_bought_back_amount * self.sold_bought_back_price
            end_transactions = [
                # sold the bought
                Transaction(
                    account=self.account,
                    date=self.finished, action='卖出', stock=self.bought_stock, amount=self.bought_amount,
                    price=self.bought_sold_price, total_money=self.bought_sold_total
                ),
                # bought the sold
                Transaction(
                    account=self.account,
                    date=self.finished, action='买入', stock=self.sold_stock, amount=actual_bought_back_amount,
                    price=self.sold_bought_back_price, total_money=actual__bought_back_total
                ),
            ]
            if self.transactions.all().count() < 4:
                for t in end_transactions:
                    t.save()
                    self.transactions.add(t)
        transactions = start_transactions + end_transactions
        return transactions
    
    @property
    def same_direction(self):
        return self.sold_stock == self.pair.started_stock
    

class Stock(models.Model):
    """一直股票，基金……"""
    code = models.CharField(max_length=6)
    market = models.CharField(max_length=2)
    name = models.CharField(max_length=10)
    is_stock = models.BooleanField(default=True)

    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    price_updated = models.DateTimeField(null=True, blank=True)
    star = models.BooleanField(default=False, blank=True)

    watching = models.BooleanField(default=False, blank=True)
    tracking = models.BooleanField(default=False, blank=True)
    comment = models.TextField(blank=True)

    pair_stocks = models.ManyToManyField('Stock', blank=True, through=StockPair)

    class Meta:
        ordering = ['-star', ]

    def __str__(self):
        return '%s(%s%s)' % (self.name, self.market, self.code)

    def update_price(self, price):
        if self.market == 'hk':
            price = Decimal(price) * Decimal('0.9')
        self.price = price
        self.price_updated = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('stock_details', args=(self.code,))

    @property
    def status(self):
        if not self.comment:
            return {}
        items = self.comment.split('~')
        return {
            'price': items[3],
            'price_change': items[4],
            'price_change_percent': items[5],
        }

    def save(self, **kwargs):
        if self.star and not self.watching:
            self.watching = True
        super(Stock, self).save(**kwargs)

    @property
    def price_file(self):
        prices_dir = os.path.join(settings.DATA_DIR, 'prices')
        if not os.path.exists(prices_dir):
            os.makedirs(prices_dir)
        return os.path.join(prices_dir, '{}.txt'.format(self.code))

    def latest_price_date(self, fp=None):
        if not fp:
            fp = open(self.price_file, 'r')
        first_line = fp.readline()
        date_item = first_line.split()[0]
        if len(date_item) < 10:  # 2000-01-01
            date_item = first_line.split()[1]
        return date_item

    def fix_tushare_price_content(self, content):
        """
        tushare的价格数据的数据头要去掉，只保留数据
        index    date    open   close    high    low      volume     code
        """
        lines = content.splitlines()
        while not lines[0][0].isdigit():
            lines = lines[1:]
        return '\n'.join(lines)

    def download_price_history(self):
        import tushare as ts
        now = timezone.now()
        target_file = self.price_file
        if os.path.exists(target_file):
            # 已经有数据，无需从上市开始下载数据
            fp = open(target_file, 'r+')
            latest_price_date = self.latest_price_date(fp=fp)
            start = datetime.strptime(latest_price_date, '%Y-%m-%d') + timedelta(days=1)
            if now.hour < 15:
                end = (now - timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                end = now.strftime('%Y-%m-%d')
            data = ts.get_h_data(self.code, autype=None, retry_count=5, start=start.strftime('%Y-%m-%d'), end=end)
            if data is not None:
                content = data.to_string()
                content = self.fix_tushare_price_content(content)
                if content:
                    fp.seek(0, 0)
                    old_content = fp.read()
                    fp.seek(0, 0)
                    fp.tell()
                    fp.write(content + old_content)
                    fp.close()
        else:
            start = '2013-01-01'
            data = ts.get_k_data(self.code, autype=None, retry_count=5, start=start, end=now.strftime('%Y-%m-%d'))
            if data is not None:
                content = data.to_string()
                content = self.fix_tushare_price_content(content)
                open(target_file, 'w').write(content)

    @property
    def get_prices(self):
        """字典形式的价格数据 {date: price}"""
        if getattr(self, '_prices', None):
            return self._prices
        prices_data = open(self.price_file, 'r')
        lines = prices_data.readlines()
        prices = {}
        for line in lines:
            items = line.split()
            prices.update({items[1]: items[3]})
        self._prices = prices
        return prices

    def get_price_by_date(self, date):
        """给定日期获得价格，如果当天不是交易日则向前寻找最近的收盘价。"""
        if getattr(date, 'strftime', None):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date
            date = datetime.strptime(date, '%Y-%m-%d')
        # add tzinfo
        date = timezone.datetime(date.year, date.month, date.day, tzinfo=timezone.get_current_timezone())
        prices = self.get_prices
        price = prices.get(date_str, None)
        while not price and date > timezone.datetime(2013, 1, 1, tzinfo=timezone.get_default_timezone()):
            date = date - timedelta(days=1)
            return self.get_price_by_date(date)
        return Decimal(price)


class BoughtSoldTransaction(models.Model):
    """以短期内卖出为目的的交易"""
    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.PROTECT, related_name='bs_transactions'
    )
    bought_stock = models.ForeignKey(
        'Stock', verbose_name='买入股票', limit_choices_to={'star': True},
        related_name='bs_transactions', on_delete=models.PROTECT
    )
    bought_price = models.DecimalField('买入价格', max_digits=10, decimal_places=4, null=True, blank=True)
    bought_amount = models.IntegerField('买入数量',)
    started = models.DateTimeField('交易时间', null=True, blank=True)
    finished = models.DateTimeField('结束交易时间', null=True, blank=True)
    sold_price = models.DecimalField('卖出价格', max_digits=10, decimal_places=4, null=True, blank=True)
    profit = models.DecimalField('利润', max_digits=10, decimal_places=4, null=True, blank=True)
    interest_rate = models.DecimalField('利率成本', max_digits=6, decimal_places=4, default='0.07')
    archived = models.BooleanField('存档-不再计算盈亏', default=False)
    transactions = models.ManyToManyField(Transaction, editable=False)

    def __str__(self):
        return '{} 交易'.format(self.bought_stock)

    @property
    def sold_total(self):
        if self.finished:
            return self.sold_price * self.bought_amount
        return self.bought_amount * self.bought_stock.price

    @property
    def bought_total(self):
        return self.bought_price * self.bought_amount

    @property
    def total(self):
        """买入卖出两笔交易的总交易额"""
        total = self.sold_total + self.bought_total
        return total

    @property
    def profit_before_fee(self):
        return self.sold_total - self.bought_total

    @property
    def money_taken(self):
        return self.bought_total

    @property
    def percent(self):
        return '%.2f%%' % (self.get_profit() / self.money_taken * 100)

    @property
    def fee(self):
        return self.total * Decimal('0.001')

    @property
    def interest(self):
        """利息额"""
        if self.finished:
            days = (self.finished - self.started).days
        else:
            days = (timezone.now() - self.started).days
        return self.bought_total * self.interest_rate / Decimal('365') * Decimal(days)

    def get_profit(self):
        if self.finished and self.profit:
            return self.profit

        profit = self.profit_before_fee - self.fee - self.interest
        return profit

    def save(self, **kwargs):
        """如果信息足够，计算利润"""
        if not self.profit and self.finished:
            self.profit = self.get_profit()
        super(BoughtSoldTransaction, self).save(**kwargs)
        self.as_transactions()

    def as_transactions(self):
        """
        把买入卖出以两笔Transaction交易的形式显示
        (如果没完成的话就是一笔卖出交易)
        """
        start_transactions = [
            # bought
            Transaction(
                account=self.account,
                date=self.started, action='买入', stock=self.bought_stock, amount=self.bought_amount,
                price=self.bought_price, total_money=self.bought_total),
        ]
        if self.transactions.all().count() < 1:
            for t in start_transactions:
                t.save()
                self.transactions.add(t)
        end_transactions = []
        if self.finished:
            end_transactions = [
                # sold
                Transaction(
                    account=self.account,
                    date=self.finished, action='卖出', stock=self.bought_stock, amount=self.bought_amount,
                    price=self.sold_price, total_money=self.sold_total)
            ]
            if self.transactions.all().count() < 2:
                for t in end_transactions:
                    t.save()
                    self.transactions.add(t)
        transactions = start_transactions + end_transactions
        return transactions


class AccountStock(models.Model):
    """账户当前持有的股票"""
    stock = models.ForeignKey(Stock, limit_choices_to={'star': True}, on_delete=models.PROTECT)
    amount = models.IntegerField()
    account = models.ForeignKey('Account', related_name='stocks', on_delete=models.PROTECT)

    @property
    def total(self):
        return self.stock.price * self.amount

    @property
    def percent(self):
        return self.total / self.account.stocks_total * Decimal(100)


class AccountStocksRange(models.Model):
    account = models.ForeignKey('Account', related_name='stocks_ranges', on_delete=models.PROTECT)
    stocks = models.ManyToManyField('Stock', limit_choices_to={'star': True}, null=True, blank=True)
    low = models.DecimalField(default='20', max_digits=5, decimal_places=2, null=True, blank=True)
    high = models.DecimalField(default='20', max_digits=5, decimal_places=2, null=True, blank=True)
    
    @property
    def mid(self):
        if self.high and self.low:
            return (self.high + self.low) / 2
    
    @property
    def account_stocks(self):
        if self.stocks.all():
            account_stocks = self.account.stocks.filter(stock__in=self.stocks.all())
        else:
            stocks_in_ranges = self.account.stocks_ranges.exclude(stocks=None).values_list('stocks', flat=True)
            account_stocks = self.account.stocks.exclude(stock__in=stocks_in_ranges)
        return account_stocks
        
    @property
    def current_values(self):
        total = Decimal(0)
        percent = Decimal(0)
        account_stocks = self.account_stocks
        for account_stock in account_stocks:
            total += account_stock.total
            percent += account_stock.percent
        if percent > self.high:
            status = '超'
            status_amount = percent - self.high
        elif percent < self.low:
            status = '低'
            status_amount = self.low - percent
        else:
            status = '正常'
            status_amount = 0
        return {
            'percent': percent,
            'total': total,
            'status': status,
            'status_amount': status_amount,
        }


class Account(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True, db_index=True)
    main = models.BooleanField('是否主账户', default=False)
    public = models.BooleanField('是否公开', default=False)
    display_summary = models.BooleanField('是否默认显示概览', default=False)
    initial_investment = models.DecimalField('初始投资', max_digits=14, decimal_places=2, null=True, blank=True)
    cash = models.DecimalField('现金', max_digits=14, decimal_places=2, default=0)
    initial_date = models.DateField('初始投资时间', )
    debt = models.DecimalField('负债', max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.sub_accounts_debt and (self.debt != self.sub_accounts_debt):
            self.debt = self.sub_accounts_debt
        super(Account, self).save(*args, **kwargs)

    @property
    def sub_accounts_asset(self):
        return self.subaccount_set.all().aggregate(Sum('asset'))['asset__sum'] or 0

    @property
    def sub_accounts_debt(self):
        return self.subaccount_set.all().aggregate(Sum('debt'))['debt__sum'] or 0

    @property
    def stocks_total(self):
        """持有的股票的市值"""
        return sum([stock.total for stock in self.stocks.all()])

    @property
    def total(self):
        """股票、子账户、现金合计"""
        return self.stocks_total + self.sub_accounts_asset + self.cash

    @property
    def net(self):
        """减去负债之后的净资产"""
        return self.total - self.debt

    @property
    def ratio(self):
        """担保比，不会翻译，暂时就写ratio吧"""
        return self.total / self.debt * Decimal(100)

    @property
    def total_yield(self):
        """总收益率"""
        return (self.net / self.initial_investment) - 1

    @property
    def total_yield_percent(self):
        """总收益率， 百分比"""
        return self.total_yield * Decimal(100)

    @property
    def years(self):
        """账户年龄"""
        initial = self.initial_date
        days = (
            timezone.now() - timezone.datetime(initial.year, initial.month, initial.day,
                                               tzinfo=timezone.get_current_timezone()
                                               )
        ).days
        years = Decimal(days) / Decimal(365)
        return years

    @property
    def yearly_yield(self):
        """用总收益率和年龄计算年化收益率"""
        years = self.years
        return (self.total_yield + 1) ** (Decimal('1')/Decimal(years)) - Decimal(1)

    @property
    def yearly_yield_percent(self):
        """年化收益率，百分比"""
        return self.yearly_yield * Decimal(100)

    def take_snapshot(self):
        """制作一个账户快照account snapshot"""
        if self.snapshots.all():
            serial_number = 1 + self.snapshots.all().order_by('-serial_number')[0].serial_number
        else:
            serial_number = 1
        snapshot = Snapshot(
            account=self,
            date=datetime.today(),
            serial_number=serial_number,
            stocks_asset=self.stocks_total,
            sub_accounts_asset=self.sub_accounts_asset,
            net_asset=self.net,
            cash=self.cash,
            debt=self.debt,
        )
        snapshot.save()
        snapshot = Snapshot.objects.get(id=snapshot.id)
        for account_stock in self.stocks.all():
            stock = account_stock.stock
            SnapshotStock.objects.create(
                snapshot=snapshot,
                stock=stock,
                amount=account_stock.amount,
                price=stock.price,
                name=stock.name,
                code=stock.code,
                total=account_stock.total
            )
        snapshot.calculate_net_asset()
        snapshot.save()

    def find_transactions(self, start, end):
        """找到账户在给定时间段内的交易"""
        transactions = self.transactions.filter(date__gte=start, date__lte=end)
        transactions = sorted(transactions, key=lambda x: x.date, reverse=True)
        return transactions

    def recent_transactions(self):
        """最近交易，返回一个月内的，如果没有交易则返回上个月的。"""
        today = timezone.now().date() + timedelta(days=1)
        month_start = timezone.datetime(today.year, today.month, 1).date()
        transactions = self.find_transactions(month_start, today)
        if not transactions:
            last_month = month_start - timedelta(days=1)
            last_month_start = timezone.datetime(last_month.year, last_month.month, 1).date()
            self.find_transactions(last_month_start, last_month)
        return transactions


class SubAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    name = models.CharField(max_length=64)
    order = models.IntegerField(default=100)
    asset = models.PositiveIntegerField('资产', default=0)
    debt = models.PositiveIntegerField('负债', default=0)

    def net_asset(self):
        return self.asset - self.debt

    def __str__(self):
        return '{} ({}子账户)'.format(self.name, self.account)

    class Meta:
        ordering = ['order']


class Snapshot(models.Model):
    """账户快照，保存一个账户在某个时间点的净资产，持有股票等等"""
    account = models.ForeignKey('Account', related_name='snapshots', on_delete=models.PROTECT)
    date = models.DateField('时间', )
    serial_number = models.PositiveIntegerField(null=True)

    net_asset = models.DecimalField('净资产', max_digits=14, decimal_places=2, null=True, blank=True)
    stocks_asset = models.DecimalField('股票市值', max_digits=14, decimal_places=2, null=True, blank=True)
    sub_accounts_asset = models.DecimalField('子账户市值', max_digits=14, decimal_places=2, blank=True, default=0)
    cash = models.DecimalField('现金', max_digits=14, decimal_places=2, null=True, blank=True)
    debt = models.DecimalField('负债', max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    increase = models.DecimalField('涨幅', max_digits=8, decimal_places=4, null=True, blank=True)
    has_transaction = models.BooleanField('是否有交易', default=False)
    transactions_count = models.IntegerField(default=0)

    error = models.DecimalField('误差', max_digits=8, decimal_places=2, null=True, blank=True)
    comment = models.TextField('备注', blank=True, default='')
    status_image = models.ImageField(upload_to='snapshots', blank=True)
    change_image = models.ImageField(upload_to='snapshots', blank=True)
    xueqiu_url = models.URLField(null=True, blank=True)
    extra_content = MarkdownxField('更多内容', blank=True, default='')

    is_annual = models.BooleanField(default=False)

    def __str__(self):
        return '{} snapshot {} '.format(self.account, self.serial_number)

    @property
    def public(self):
        return self.account.public

    @property
    def previous_snapshot(self):
        """找到上一个快照"""
        previous_snapshot = None
        previous_snapshots = self.account.snapshots.all().filter(id__lt=self.id).order_by('-id')
        if previous_snapshots.exists():
            previous_snapshot = previous_snapshots[0]
        return previous_snapshot

    def calculate_increase(self):
        """比上一个快照的净资产变动"""
        self.increase = 0
        previous_snapshot = self.previous_snapshot
        if previous_snapshot:
            self.increase = self.net_asset / previous_snapshot.net_asset - 1

    def calculate_net_asset(self):
        """计算净资产等等"""
        for stock in self.stocks.all():
            if not (stock.total and stock.name and stock.code):
                stock.total = stock.price * stock.amount
                stock.name = stock.stock.name
                stock.code = stock.stock.code
                stock.save()
        self.stocks_asset = sum([stock.total for stock in self.stocks.all()])
        self.net_asset = self.total - (self.debt or 0)
        if not self.transactions_count:
            self.transactions_count = len(self.find_transactions())
        self.calculate_increase()

    def populate_from_previous(self):
        """快捷方式，从上一个快照复制股票过来"""
        if self.stocks.all():
            return
        previous = self.previous_snapshot
        for snapshot_stock in previous.stocks.all():
            snapshot_stock.id = None
            snapshot_stock.total = None
            snapshot_stock.snapshot = self
            snapshot_stock.save()

    @property
    def increase_percent(self):
        """比上一个快照的净资产变动，百分比"""
        return self.increase * 100

    @property
    def all_time_increase(self):
        """比初始投资的净资产变动"""
        return self.net_asset / self.account.initial_investment - 1

    @property
    def all_time_increase_percent(self):
        """比初始投资的净资产变动，百分比"""
        return self.all_time_increase * 100

    @property
    def total(self):
        """总资产"""
        return self.stocks_asset + self.sub_accounts_asset + self.cash

    def find_transactions(self):
        """找到当月1日到snapshot日期的交易"""
        start = timezone.datetime(self.date.year, self.date.month, 1).date()
        transactions = self.account.find_transactions(start, self.date)
        return transactions

    def formatted_extra_content(self):
        return markdownify(self.extra_content)

    # 下面是年度snapshot用到的代码

    @property
    def previous_annual_snapshot(self):
        """找到上一个快照"""
        previous_annual_snapshot = None
        previous_annual_snapshots = self.account.snapshots.all().filter(id__lt=self.id, is_annual=True).order_by('-id')
        if previous_annual_snapshots.exists():
            previous_annual_snapshot = previous_annual_snapshots[0]
        return previous_annual_snapshot

    @property
    def yield_yoy(self):
        """一年收益率, 只适用于 annual_snapshot """
        if not self.is_annual:
            return None
        return self.net_asset / self.previous_annual_snapshot.net_asset - 1

    @property
    def yield_yoy_percent(self):
        """一年收益率，百分比"""
        return self.yield_yoy * 100

    @property
    def nth_year(self):
        first_snapshot = self.account.snapshots.all().order_by('id')[0]
        return self.date.year - first_snapshot.date.year

    @property
    def age(self):
        """snapshot时的账户年龄"""
        initial = self.account.initial_date
        age = self.date - datetime(initial.year, initial.month, initial.day).date() + timedelta(days=2)
        return td_format(age)

    @property
    def stocks_ordered(self):
        return self.stocks.order_by('-total')


class SnapshotStock(models.Model):
    """账户快照 当时持有的股票"""
    snapshot = models.ForeignKey('Snapshot', related_name='stocks', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, limit_choices_to={'star': True})
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    name = models.CharField(max_length=16, blank=True)
    code = models.CharField(max_length=6, blank=True)
    total = models.DecimalField('总价', max_digits=14, decimal_places=2, null=True, blank=True)

    @property
    def get_total(self):
        return self.price * self.amount

    @property
    def percent(self):
        """占快照当时持有股票的百分比"""
        return self.total / self.snapshot.stocks_asset * Decimal(100)

    @property
    def current_total(self):
        return self.stock.price * self.amount
