# -*- coding: UTF-8 -*-
"""
券商有时候给出四舍五入的均价，自动计算交易额的时候，可能造成成交额有一点误差。
"""
from decimal import Decimal
from datetime import timedelta, datetime
from django.utils import timezone

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q

from stocks.utils import update_stocks_prices


'''
分红处理代码
from decimal import Decimal
stock = Stock.objects.get(code='600816')
trans = PairTransaction.objects.filter(finished__isnull=True, bought_stock=stock)
for transaction in trans:
    transaction.bought_price -= Decimal('0.5')
    transaction.save()

sold_trans = PairTransaction.objects.filter(finished__isnull=True, sold_stock=stock)
for transaction in sold_trans:
    transaction.sold_price -= Decimal('0.5')
    transaction.save()


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


class Transaction(models.Model):
    """一笔买入、卖出交易"""
    BUY = u'买入'
    SELL = u'卖出'
    ACTION_CHOICES = (
        (BUY, BUY),
        (SELL, SELL),
    )
    account = models.ForeignKey('Account', blank=True, null=True, on_delete=models.PROTECT, related_name='transactions')
    action = models.CharField(u'交易类型', max_length=16, blank=True, choices=ACTION_CHOICES)
    stock = models.ForeignKey(
        'Stock', verbose_name=u'股票', limit_choices_to={'star': True},
        related_name='transactions', on_delete=models.PROTECT
    )
    price = models.DecimalField(u'交易价格', max_digits=10, decimal_places=4, null=True, blank=True)
    amount = models.IntegerField(u'交易数量',)
    date = models.DateTimeField(u'交易时间', null=True, blank=True)
    total_money = models.DecimalField(u'交易额', max_digits=10, decimal_places=4, null=True, blank=True)
    has_updated_account = models.BooleanField(u'是否已经更新账户', default=False)

    def save(self, *args, **kwargs):
        u"""如果没有填交易额，在save之前自动计算。"""
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
    u"""一组配对交易标的"""
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

    def __unicode__(self):
        if not self.name:
            self.name = u'{}/{}'.format(self.started_stock.name, self.target_stock.name)
            self.save()
        return self.name

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
    def status(self):
        """计算配对今日的涨跌幅"""
        change_one = Decimal(self.started_stock.status['price_change_percent'])
        change_two = Decimal(self.target_stock.status['price_change_percent'])
        change_percent = ((100 + change_one) / (100 + change_two) - 1) * 100
        return {
            'change_percent': change_percent
        }


class PairTransaction(models.Model):
    u"""一笔完整的配对交易"""
    account = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='pair_transactions')
    pair = models.ForeignKey(
        StockPair, limit_choices_to={'star': True}, null=True, blank=True,
        related_name='transactions', on_delete=models.PROTECT
    )
    sold_stock = models.ForeignKey(
        'Stock', verbose_name=u'卖出股票', limit_choices_to={'star': True},
        related_name='sold_pair_transactions', on_delete=models.PROTECT
    )
    sold_price = models.DecimalField(u'卖出价格', max_digits=10, decimal_places=4)
    sold_amount = models.IntegerField(u'卖出数量',)
    bought_stock = models.ForeignKey(
        'Stock', verbose_name=u'买入股票', limit_choices_to={'star': True},
        related_name='bought_pair_transactions', on_delete=models.PROTECT
    )
    bought_price = models.DecimalField(u'买入价格', max_digits=10, decimal_places=4)
    bought_amount = models.IntegerField(u'买入数量',)
    started = models.DateTimeField(u'交易时间', null=True, blank=True)
    finished = models.DateTimeField(u'结束交易时间', null=True, blank=True)
    sold_bought_back_price = models.DecimalField(
        u'卖出后买入价格', max_digits=10, decimal_places=4, null=True, blank=True
    )
    bought_back_amount = models.IntegerField(
        u'实际买回数量', null=True, blank=True,
        help_text=u'实际买回的数量可能和之前卖出的数量不一致，这个值用于显示Transaction的交易额，并不用于计算配对交易的利润。'
    )
    bought_sold_price = models.DecimalField(u'买入后卖出价格', max_digits=10, decimal_places=4, null=True, blank=True)
    profit = models.DecimalField(u'利润', max_digits=10, decimal_places=4, null=True, blank=True)
    order = models.IntegerField(default=100)
    archived = models.BooleanField(u'存档-不再计算盈亏', default=False)

    transactions = models.ManyToManyField(Transaction)

    class Meta:
        ordering = ['order', 'finished', '-started']

    def __unicode__(self):
        return u'{} 配对交易'.format(self.pair)

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
    def profit_before_fee(self):
        return self.sold_total - self.sold_bought_back_total + self.bought_sold_total - self.bought_total

    @property
    def money_taken(self):
        """占用资金"""
        return max(self.bought_total, self.sold_total)

    @property
    def percent(self):
        """利润占占用资金的百分比"""
        return '%%%.2f' % (self.get_profit() / self.money_taken * 100)

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
                date=self.started, action=u'卖出', stock=self.sold_stock, amount=self.sold_amount,
                price=self.sold_price, total_money=self.sold_total),
            # bought
            Transaction(
                account=self.account,
                date=self.started, action=u'买入', stock=self.bought_stock, amount=self.bought_amount,
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
                    date=self.finished, action=u'卖出', stock=self.bought_stock, amount=self.bought_amount,
                    price=self.bought_sold_price, total_money=self.bought_sold_total
                ),
                # bought the sold
                Transaction(
                    account=self.account,
                    date=self.finished, action=u'买入', stock=self.sold_stock, amount=actual_bought_back_amount,
                    price=self.sold_bought_back_price, total_money=actual__bought_back_total
                ),
            ]
            if self.transactions.all().count() < 4:
                for t in end_transactions:
                    t.save()
                    self.transactions.add(t)
        transactions = start_transactions + end_transactions
        return transactions


class Stock(models.Model):
    """一直股票，基金……"""
    code = models.CharField(max_length=6)
    market = models.CharField(max_length=2)
    name = models.CharField(max_length=10)
    is_stock = models.BooleanField(default=True)

    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    price_updated = models.DateTimeField(null=True, blank=True)
    star = models.BooleanField(default=False, blank=True)

    archive = models.BooleanField(default=False, blank=True)
    archived_reason = models.CharField(max_length=256, blank=True, default='')
    comment = models.TextField(blank=True)

    pair_stocks = models.ManyToManyField('Stock', blank=True, through=StockPair)

    class Meta:
        ordering = ['-star', ]

    def __unicode__(self):
        return u'%s(%s%s)' % (self.name, self.market, self.code)

    def update_price(self):
        update_stocks_prices([self])

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


class BoughtSoldTransaction(models.Model):
    """以短期内卖出为目的的交易"""
    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.PROTECT, related_name='bs_transactions'
    )
    bought_stock = models.ForeignKey(
        'Stock', verbose_name=u'买入股票', limit_choices_to={'star': True},
        related_name='bs_transactions', on_delete=models.PROTECT
    )
    bought_price = models.DecimalField(u'买入价格', max_digits=10, decimal_places=4, null=True, blank=True)
    bought_amount = models.IntegerField(u'买入数量',)
    started = models.DateTimeField(u'交易时间', null=True, blank=True)
    finished = models.DateTimeField(u'结束交易时间', null=True, blank=True)
    sold_price = models.DecimalField(u'卖出价格', max_digits=10, decimal_places=4, null=True, blank=True)
    profit = models.DecimalField(u'利润', max_digits=10, decimal_places=4, null=True, blank=True)
    interest_rate = models.DecimalField(u'利率成本', max_digits=6, decimal_places=4, default='0.0835')
    archived = models.BooleanField(u'存档-不再计算盈亏', default=False)
    transactions = models.ManyToManyField(Transaction)

    def __unicode__(self):
        return u'{} 交易'.format(self.bought_stock)

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
        return '%%%.2f' % (self.get_profit() / self.money_taken * 100)

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
                date=self.started, action=u'买入', stock=self.bought_stock, amount=self.bought_amount,
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
                    date=self.finished, action=u'卖出', stock=self.bought_stock, amount=self.bought_amount,
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
    stock = models.ForeignKey(Stock, limit_choices_to={'star': True})
    amount = models.IntegerField()
    account = models.ForeignKey('Account', related_name='stocks')

    @property
    def total(self):
        return self.stock.price * self.amount

    @property
    def percent(self):
        return self.total / self.account.total * Decimal(100)


class Account(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(unique=True, db_index=True)
    main = models.BooleanField(u'是否主账户', default=False)
    public = models.BooleanField(u'是否公开', default=False)
    display_summary = models.BooleanField(u'是否默认显示概览', default=False)
    initial_investment = models.DecimalField(u'初始投资', max_digits=14, decimal_places=2, null=True, blank=True)
    cash = models.DecimalField(u'现金', max_digits=14, decimal_places=2, default=0)
    initial_date = models.DateField(u'初始投资时间', )
    debt = models.DecimalField(u'负债', max_digits=10, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def stocks_total(self):
        """持有的股票的市值"""
        return sum([stock.total for stock in self.stocks.all()])

    @property
    def total(self):
        """股票现金合计"""
        return self.stocks_total + self.cash

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
            serial_number = 1 + self.snapshots.all().order_by('-id')[0].id
        else:
            serial_number = 1
        snapshot = Snapshot(
            account=self,
            date=datetime.today(),
            serial_number=serial_number,
            stocks_asset=self.stocks_total,
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
        today = timezone.now().date()
        month_start = timezone.datetime(today.year, today.month, 1).date()
        transactions = self.find_transactions(month_start, today)
        if not transactions:
            last_month = month_start - timedelta(days=1)
            last_month_start = timezone.datetime(last_month.year, last_month.month, 1).date()
            self.find_transactions(last_month_start, last_month)
        return transactions


class Snapshot(models.Model):
    """账户快照，保存一个账户在某个时间点的净资产，持有股票等等"""
    account = models.ForeignKey('Account', related_name='snapshots', on_delete=models.PROTECT)
    date = models.DateField(u'时间', )
    serial_number = models.PositiveIntegerField(null=True)

    net_asset = models.DecimalField(u'净资产', max_digits=14, decimal_places=2, null=True, blank=True)
    stocks_asset = models.DecimalField(u'股票市值', max_digits=14, decimal_places=2, null=True, blank=True)
    cash = models.DecimalField(u'现金', max_digits=14, decimal_places=2, null=True, blank=True)
    debt = models.DecimalField(u'负债', max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    increase = models.DecimalField(u'涨幅', max_digits=8, decimal_places=4, null=True, blank=True)
    has_transaction = models.BooleanField(u'是否有交易', default=False)
    transactions_count = models.IntegerField(default=0)

    error = models.DecimalField(u'误差', max_digits=8, decimal_places=2, null=True, blank=True)
    comment = models.TextField(u'备注', blank=True, default='')
    status_image = models.ImageField(upload_to='snapshots', blank=True)
    change_image = models.ImageField(upload_to='snapshots', blank=True)
    xueqiu_url = models.URLField(null=True, blank=True)

    def __unicode__(self):
        return u'{} snapshot {} '.format(self.account, self.serial_number)

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
        self.net_asset = self.stocks_asset + self.cash - (self.debt or 0)
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
    def total(self):
        """总资产"""
        return self.stocks_total + self.cash

    def find_transactions(self):
        """找到当月1日到snapshot日期的交易"""
        start = timezone.datetime(self.date.year, self.date.month, 1).date()
        transactions = self.account.find_transactions(start, self.date)
        return transactions


class SnapshotStock(models.Model):
    """账户快照 当时持有的股票"""
    snapshot = models.ForeignKey('Snapshot', related_name='stocks')
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, limit_choices_to={'star': True})
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    name = models.CharField(max_length=16, blank=True)
    code = models.CharField(max_length=6, blank=True)
    total = models.DecimalField(u'总价', max_digits=14, decimal_places=2, null=True, blank=True)

    @property
    def get_total(self):
        return self.stock.price * self.amount

    @property
    def percent(self):
        """占快照当时持有股票的百分比"""
        return self.total / self.snapshot.stocks_asset * Decimal(100)
