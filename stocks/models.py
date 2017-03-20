# -*- coding: UTF-8 -*-
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


class StockPair(models.Model):
    name = models.CharField(max_length=256, default='')
    started_stock = models.ForeignKey('Stock', limit_choices_to={'star': True}, related_name='pairs', on_delete=models.PROTECT)
    target_stock = models.ForeignKey('Stock', limit_choices_to={'star': True}, related_name='targeted_pairs', on_delete=models.PROTECT)
    star = models.BooleanField(default=False, blank=True)
    current_value = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    value_updated = models.DateTimeField(null=True, blank=True)

    order = models.IntegerField(default=100)

    class Meta:
        ordering = ['star', 'order']

    def __unicode__(self):
        if not self.name:
            self.name = u'{}/{}'.format(self.started_stock.name, self.target_stock.name )
            self.save()
        return self.name

    def update(self):
        if not self.started_stock.price or not self.target_stock.price:
            return
        if not self.value_updated or self.started_stock.price_updated > self.value_updated or self.target_stock.price_updated > self.value_updated:
            self.current_value = self.started_stock.price / self.target_stock.price
            self.value_updated = timezone.now()
            self.save()

    def update_if_needed(self):
        if not self.value_updated or self.value_updated < (timezone.now() + timedelta(minutes=1)):
            self.update()


class PairTransaction(models.Model):
    account = models.ForeignKey('Account', on_delete=models.PROTECT, related_name='pair_transactions')
    pair = models.ForeignKey(StockPair, limit_choices_to={'star': True}, null=True, blank=True, related_name='transactions', on_delete=models.PROTECT)
    sold_stock = models.ForeignKey('Stock', verbose_name=u'卖出股票', limit_choices_to={'star': True}, related_name='sold_pair_transactions', on_delete=models.PROTECT)
    sold_price = models.DecimalField(u'卖出价格', max_digits=10, decimal_places=4)
    sold_amount = models.IntegerField(u'卖出数量',)
    bought_stock = models.ForeignKey('Stock', verbose_name=u'买入股票', limit_choices_to={'star': True}, related_name='bought_pair_transactions', on_delete=models.PROTECT)
    bought_price = models.DecimalField(u'买入价格', max_digits=10, decimal_places=4)
    bought_amount = models.IntegerField(u'买入数量',)
    started = models.DateTimeField(u'交易时间', null=True, blank=True)

    finished = models.DateTimeField(u'结束交易时间', null=True, blank=True)
    sold_bought_back_price = models.DecimalField(u'卖出后买入价格', max_digits=10, decimal_places=4, null=True, blank=True)
    bought_sold_price = models.DecimalField(u'买入后卖出价格', max_digits=10, decimal_places=4, null=True, blank=True)
    profit = models.DecimalField(u'利润', max_digits=10, decimal_places=4, null=True, blank=True)
    order = models.IntegerField(default=100)

    class Meta:
        ordering = ['order', 'finished', '-started']

    def __unicode__(self):
        return u'{} 配对交易'.format(self.pair)

    @property
    def sold_total(self):
        return self.sold_price * self.sold_amount

    @property
    def bought_total(self):
        return self.bought_price* self.bought_amount

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
        total = self.sold_total + self.sold_bought_back_total + self.bought_sold_total + self.bought_total
        return total

    @property
    def profit_before_fee(self):
        return self.sold_total - self.sold_bought_back_total + self.bought_sold_total - self.bought_total

    @property
    def money_taken(self):
        return max(self.bought_total, self.sold_total)

    @property
    def percent(self):
        return '%%%.2f' % (self.get_profit() / self.money_taken * Decimal(100))

    @property
    def fee(self):
        return self.total * Decimal('0.001')

    def get_profit(self):
        if self.finished and self.profit:
            return self.profit

        profit = self.profit_before_fee - self.fee
        return profit

    @property
    def to_ratio(self):
        if self.sold_stock == self.pair.started_stock:
            ratio = self.sold_price / self.bought_price
        else:
            ratio = self.bought_price / self.sold_price
        return ratio

    @property
    def from_ratio(self):
        if self.finished:
            if self.sold_stock == self.pair.started_stock:
                ratio = self.sold_bought_back_price / self.bought_sold_price
            else:
                ratio = self.bought_sold_price / self.sold_bought_back_price
            return ratio

    def save(self, **kwargs):
        if not self.pair:
            pair = StockPair.objects.filter(
                Q(started_stock=self.sold_stock, target_stock = self.bought_stock)|Q(started_stock=self.bought_stock, target_stock = self.sold_stock)
            )
            if not pair.exists():
                pair = StockPair.objects.create(started_stock=self.sold_stock, target_stock = self.bought_stock)
            else:
                pair = pair[0]
            pair.star = True
            pair.save()
            self.pair = pair

        if not self.profit and self.finished:
            self.profit = self.get_profit()
        super(PairTransaction, self).save(**kwargs)


class Stock(models.Model):
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


class Transaction(models.Model):
    account = models.ForeignKey('Account', blank=True, null=True, on_delete=models.PROTECT, related_name='transactions')
    bought_stock = models.ForeignKey('Stock', verbose_name=u'买入股票', limit_choices_to={'star': True}, related_name='transactions', on_delete=models.PROTECT)
    bought_price = models.DecimalField(u'买入价格', max_digits=10, decimal_places=4, null=True, blank=True)
    bought_amount = models.IntegerField(u'买入数量',)
    started = models.DateTimeField(u'交易时间', null=True, blank=True)
    finished = models.DateTimeField(u'结束交易时间', null=True, blank=True)
    sold_price = models.DecimalField(u'卖出价格', max_digits=10, decimal_places=4, null=True, blank=True)
    profit = models.DecimalField(u'利润', max_digits=10, decimal_places=4, null=True, blank=True)
    interest_rate = models.DecimalField(u'利率成本', max_digits=6, decimal_places=4, default='0.0835')

    def __unicode__(self):
        return u'{} 交易'.format(self.bought_stock)

    @property
    def sold_total(self):
        if self.finished:
            return self.sold_price * self.bought_amount
        return self.bought_amount * self.bought_stock.price

    @property
    def bought_total(self):
        return self.bought_price* self.bought_amount

    @property
    def total(self):
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
        return '%%%.2f' % (self.get_profit() / self.money_taken * Decimal(100))

    @property
    def fee(self):
        return self.total * Decimal('0.001')

    @property
    def interest(self):
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
        if not self.profit and self.finished:
            self.profit = self.get_profit()
        super(Transaction, self).save(**kwargs)


class AccountStock(models.Model):
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
        return sum([stock.total for stock in self.stocks.all()])

    @property
    def total(self):
        return self.stocks_total + self.cash

    @property
    def net(self):
        return self.total - self.debt

    @property
    def ratio(self):
        return self.total / self.debt * Decimal(100)

    @property
    def total_yield(self):
        return (self.net / self.initial_investment) - 1

    @property
    def total_yield_percent(self):
        return self.total_yield * Decimal(100)

    @property
    def years(self):
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
        years = self.years
        return (self.total_yield + 1) ** (Decimal('1')/Decimal(years)) - Decimal(1)

    @property
    def yearly_yield_percent(self):
        return self.yearly_yield * Decimal(100)

    def take_snapshot(self):
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
        for account_stock in self.stocks.all():
            stock = account_stock.stock
            snapshot_stock = SnapshotStock.objects.create(
                snapshot=snapshot,
                stock=stock,
                amount=account_stock.amount,
                price=stock.price,
                name=stock.name,
                code=stock.code,
                total=account_stock.total
            )


class Snapshot(models.Model):
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
        previous_snapshot = None
        previous_snapshots = self.account.snapshots.all().filter(id__lt=self.id).order_by('-id')
        if previous_snapshots.exists():
            previous_snapshot = previous_snapshots[0]
        return previous_snapshot

    def calculate_increase(self):
        self.increase = 0
        previous_snapshot = self.previous_snapshot
        if previous_snapshot:
            self.increase = self.net_asset / previous_snapshot.net_asset - 1

    def calculate_net_asset(self):
        for stock in self.stocks.all():
            if not (stock.total and stock.name and stock.code):
                stock.total = stock.price * stock.amount
                stock.name = stock.stock.name
                stock.code = stock.stock.code
                stock.save()
        self.stocks_asset = sum([stock.total for stock in self.stocks.all()])
        self.net_asset = self.stocks_asset + self.cash - (self.debt or 0)
        self.calculate_increase()

    def populate_from_previous(self):
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
        return self.increase * 100

    @property
    def total(self):
        return self.stocks_total + self.cash


class SnapshotStock(models.Model):
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
        return self.total / self.snapshot.stocks_asset * Decimal(100)

