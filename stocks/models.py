# -*- coding: UTF-8 -*-
from decimal import Decimal
from datetime import timedelta
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
    started_stock = models.ForeignKey('Stock', limit_choices_to={'star': True}, related_name='pairs')
    target_stock = models.ForeignKey('Stock', limit_choices_to={'star': True}, related_name='targeted_pairs')
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
    pair = models.ForeignKey(StockPair, limit_choices_to={'star': True}, null=True, blank=True, related_name='transactions')
    sold_stock = models.ForeignKey('Stock', verbose_name=u'卖出股票', limit_choices_to={'star': True}, related_name='sold_pair_transactions')
    sold_price = models.DecimalField(u'卖出价格', max_digits=10, decimal_places=4)
    sold_amount = models.IntegerField(u'卖出数量',)
    bought_stock = models.ForeignKey('Stock', verbose_name=u'买入股票', limit_choices_to={'star': True}, related_name='bought_pair_transactions')
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
    bought_stock = models.ForeignKey('Stock', verbose_name=u'买入股票', limit_choices_to={'star': True}, related_name='transactions')
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
    initial_date = models.DateField(u'初始投资时间', )
    debt = models.DecimalField(u'负债', max_digits=10, decimal_places=2, null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def total(self):
        return sum([stock.total for stock in self.stocks.all()])

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

