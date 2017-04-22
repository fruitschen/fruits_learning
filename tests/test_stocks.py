# -*- coding: UTF-8 -*-
import pytest
from stocks.models import *
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
pytestmark = pytest.mark.django_db


def test_stock(client):
    assert(Account.objects.all().count() == 0)
    account = Account.objects.create(
        name='test',
        slug='test',
        main=True,
        public=True,
        initial_investment=100000,
        cash=0,
        initial_date=datetime.today(),
        debt=0,
    )
    assert (Account.objects.all().count() == 1)
    assert (Stock.objects.all().count() == 0)
    gree_stock = Stock.objects.create(
        code='000651',
        market='sz',
        name=u'格力电器',
        price=40,
    )
    anxin_stock = Stock.objects.create(
        code='600816',
        market='sh',
        name=u'安信信托',
        price=20,
    )
    assert (Stock.objects.all().count() == 2)

    assert account.stocks_total == 0
    assert account.total == 0
    transaction = Transaction.objects.create(
        stock=gree_stock,
        action=Transaction.BUY,
        amount=100,
        price=Decimal('20'),
        account=account,
        date=datetime(2017, 1, 1, tzinfo=timezone.get_current_timezone()),
    )
    '''
    AccountStock.objects.create(
        stock=gree_stock, amount=100, account=account,
    )
    '''
    assert account.stocks_total == Decimal('4000')
    assert account.total == Decimal('4000')
    account.cash = 1000
    assert account.stocks_total == Decimal('4000')
    assert account.total == Decimal('5000')
    AccountStock.objects.create(
        stock=anxin_stock, amount=100, account=account,
    )
    assert account.stocks_total == Decimal('6000')
    assert account.total == Decimal('7000')
    gree_stock.price = Decimal('50')
    gree_stock.save()
    assert account.stocks_total == Decimal('7000')
    assert account.total == Decimal('8000')

    transaction = Transaction.objects.create(
        account=account,
        action=Transaction.BUY,
        stock=gree_stock,
        price=Decimal('20'),
        amount=100,
        date=datetime(2017, 1, 1, tzinfo=timezone.get_current_timezone()),
    )
    assert transaction.total_money == Decimal(2000)
    assert transaction.has_updated_account == True
    assert account.stocks_total == Decimal('12000')
    assert account.total == Decimal('13000')

    transaction = Transaction.objects.create(
        account=account,
        action=Transaction.SELL,
        stock=gree_stock,
        price=Decimal('20'),
        amount=100,
        date=datetime(2017, 2, 1, tzinfo=timezone.get_current_timezone()),
    )
    assert account.stocks_total == Decimal('7000')
    assert account.total == Decimal('8000')

    transaction = Transaction.objects.create(
        account=account,
        action=Transaction.BUY,
        stock=gree_stock,
        price=Decimal('20'),
        amount=100,
        date=datetime(2017, 2, 1, tzinfo=timezone.get_current_timezone()),
        has_updated_account=True,
    )
    assert account.stocks_total == Decimal('7000')
    assert account.total == Decimal('8000')

    bs_transaction = BoughtSoldTransaction.objects.create(
        account=account,
        bought_stock=gree_stock,
        bought_price=Decimal('20'),
        bought_amount=100,
        started=timezone.datetime(2017, 2, 1, tzinfo=timezone.get_current_timezone()),
        finished=timezone.datetime(2017, 2, 2, tzinfo=timezone.get_current_timezone()),
        sold_price=Decimal('21'),
        interest_rate=Decimal('0.1'),  # 10% per year
    )
    assert bs_transaction.fee == (Decimal('2000') + Decimal('2100') ) * Decimal('0.001')
    assert bs_transaction.interest == Decimal('2000') * Decimal('0.1') / Decimal('365')
    assert bs_transaction.get_profit() == Decimal('100') - bs_transaction.fee - bs_transaction.interest

