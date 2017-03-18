# -*- coding: UTF-8 -*-
from decimal import Decimal
import json
import os.path
from datetime import datetime, date, timedelta


from django.db.models import Sum, Q
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseForbidden

from stocks.models import Stock, StockPair, PairTransaction, Transaction, Account
from stocks.utils import update_stocks_prices, update_stocks_prices_url


def stocks(request):
    logged_in = request.user.is_authenticated()
    star_stocks = Stock.objects.all().filter(star=True)
    if logged_in:
        accounts = Account.objects.all()
    else:
        accounts = Account.objects.filter(public=True)
    context = {
        'star_stocks': star_stocks,
        'accounts': accounts,
    }
    if logged_in:
        context.update(get_pairs_context(request))
    return render(request, 'stocks/stocks.html', context)


def account_details(request, account_slug):
    logged_in = request.user.is_authenticated()
    account = Account.objects.get(slug=account_slug)
    if not account.public and not request.user.is_authenticated():
        return HttpResponseForbidden('Oops')
    now = timezone.now()
    star_stocks = Stock.objects.all().filter(star=True)
    account_pair_transactions = account.pair_transactions.all()
    if account.public:
        recent_pair_transactions = account_pair_transactions.filter(finished__isnull=False).order_by('-finished')[:5]
    else:
        recent_pair_transactions = account_pair_transactions.filter(finished__isnull=False).order_by('-finished').exclude(finished__lt=timezone.datetime(now.year, now.month, 1))
    pair_transactions_unfinished = account_pair_transactions.filter(finished__isnull=True)
    pair_virtual_profit = 0
    for p in pair_transactions_unfinished:
        pair_virtual_profit += p.get_profit()

    account_transactions = account.transactions.all()
    transactions = account_transactions.exclude(finished__lt=timezone.datetime(now.year, now.month, 1))
    transactions_this_month = transactions.filter(finished__isnull=False).order_by('-finished')
    transactions_unfinished = transactions.filter(finished__isnull=True).order_by('-started')
    transaction_profit = transactions_this_month.aggregate(Sum('profit'))['profit__sum']
    transaction_virtual_profit = 0
    for t in transactions_unfinished:
        transaction_virtual_profit += t.get_profit()

    aggregates_by_months = []
    year_profits =  {
        'time': '{} ~ '.format(now.year, 1, 1),
        'pair_profit': 0,
        'profit': 0,
        'total': 0
    }
    month = now.month
    while month != 0:
        start = timezone.datetime(now.year, month, 1)
        end = timezone.datetime(now.year, month+1, 1)
        pair_transactions_by_month = account_pair_transactions.filter(finished__isnull=False)\
            .filter(finished__gte=start, finished__lt=end)
        transactions_by_month = account_transactions.filter(finished__isnull=False)\
            .filter(finished__gte=start, finished__lt=end)

        pair_profit_by_momth = pair_transactions_by_month.aggregate(Sum('profit'))['profit__sum'] or 0
        profit_by_momth = transactions_by_month.aggregate(Sum('profit'))['profit__sum'] or 0
        aggregates_by_months.append({
            'time': '{} ~ {}'.format(start.date(), (end-timedelta(days=1)).date()),
            'pair_profit':pair_profit_by_momth,
            'profit':profit_by_momth,
            'total': pair_profit_by_momth + profit_by_momth
        })
        year_profits['pair_profit'] += pair_profit_by_momth
        year_profits['profit'] += profit_by_momth
        year_profits['total'] += pair_profit_by_momth + profit_by_momth
        month -= 1

    aggregates_by_months.append(year_profits)

    context = {
        'account': account,
        'logged_in': logged_in,
        'star_stocks': star_stocks,
        'recent_pair_transactions': recent_pair_transactions,
        'pair_transactions_unfinished': pair_transactions_unfinished,
        'pair_virtual_profit': pair_virtual_profit,
        'account_transactions': account_transactions,
        'transactions_this_month': transactions_this_month,
        'transactions_unfinished': transactions_unfinished,
        'transaction_profit': transaction_profit,
        'transaction_virtual_profit': transaction_virtual_profit,
        'aggregates_by_months': aggregates_by_months,
        'year_profits': year_profits,
    }
    context.update(get_pairs_context(request))
    return render(request, 'stocks/account_details.html', context)


def get_pairs_context(request):
    pairs = StockPair.objects.all()
    star_pairs = StockPair.objects.filter(star=True)
    ids = star_pairs.values_list('target_stock', 'started_stock')
    stock_ids = []
    for i in ids:
        stock_ids.extend(i)
    stock_ids = set(stock_ids)

    stocks = Stock.objects.filter(id__in=stock_ids)
    if request.GET.get('force_update', False):
        update_stocks_prices(stocks)

    return {"pairs": star_pairs, "update_stocks_prices_url": update_stocks_prices_url(stocks),}


@staff_member_required
def pair_list(request):
    context = get_pairs_context(request)
    return render(request, 'stocks/includes/pair_list.html', context)


@staff_member_required
def pair_details(request, pair_id):
    pair = StockPair.objects.get(id=pair_id)
    pair_transactions = PairTransaction.objects.all().filter(pair=pair).filter(finished__isnull=False).order_by('-finished')
    unfinished_pair_transactions = PairTransaction.objects.all().filter(pair=pair).exclude(finished__isnull=False).order_by('-started')

    context = {
        'pair': pair,
        'pair_transactions': pair_transactions,
        'unfinished_pair_transactions': unfinished_pair_transactions,
    }
    return render(request, 'stocks/pair_details.html', context)
