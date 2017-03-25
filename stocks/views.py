# -*- coding: UTF-8 -*-
from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseForbidden

from stocks.models import Stock, StockPair, PairTransaction, Account
from stocks.utils import update_stocks_prices, update_stocks_prices_url
from stocks.jobs import get_price


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
    get_price_job = None
    if logged_in and request.GET.get('update', False):
        get_price_job = get_price.delay()
    account = Account.objects.get(slug=account_slug)
    if not account.public and not request.user.is_authenticated():
        return HttpResponseForbidden('Oops')
    snapshots = account.snapshots.all().order_by('-id')
    snapshots_chart_data = None
    if snapshots.count() >= 3:
        raw_data = snapshots.values_list('date', 'net_asset')
        raw_data = raw_data.reverse()
        x_axis = [r[0].strftime('%Y-%m-%d') for r in raw_data]
        y_axis = [int(r[1]) for r in raw_data]
        snapshots_chart_data = {'x_axis': x_axis, 'y_axis': y_axis}

    now = timezone.now()
    star_stocks = Stock.objects.all().filter(star=True)
    all_account_pair_transactions = account.pair_transactions.all()
    account_pair_transactions = all_account_pair_transactions.exclude(archived=True)
    if account.public:
        recent_pair_transactions = account_pair_transactions.filter(finished__isnull=False).order_by('-finished')[:5]
    else:
        recent_pair_transactions = account_pair_transactions.filter(finished__isnull=False).order_by('-finished').\
            exclude(finished__lt=timezone.datetime(now.year, now.month, 1))
    pair_transactions_unfinished = account_pair_transactions.filter(finished__isnull=True)
    pair_virtual_profit = 0
    for p in pair_transactions_unfinished:
        pair_virtual_profit += p.get_profit()

    all_account_bs_transactions = account.bs_transactions.all()
    account_bs_transactions = all_account_bs_transactions.exclude(archived=True)

    bs_transactions = account_bs_transactions.exclude(finished__lt=timezone.datetime(now.year, now.month, 1))
    bs_transactions_this_month = bs_transactions.filter(finished__isnull=False).order_by('-finished')
    bs_transactions_unfinished = bs_transactions.filter(finished__isnull=True).order_by('-started')
    transaction_profit = bs_transactions_this_month.aggregate(Sum('profit'))['profit__sum']
    transaction_virtual_profit = 0
    for t in bs_transactions_unfinished:
        transaction_virtual_profit += t.get_profit()

    aggregates_by_months = []
    year_profits = {
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
        transactions_by_month = account_bs_transactions.filter(finished__isnull=False)\
            .filter(finished__gte=start, finished__lt=end)

        pair_profit_by_momth = pair_transactions_by_month.aggregate(Sum('profit'))['profit__sum'] or 0
        profit_by_momth = transactions_by_month.aggregate(Sum('profit'))['profit__sum'] or 0
        aggregates_by_months.append({
            'time': '{} ~ {}'.format(start.date(), (end-timedelta(days=1)).date()),
            'pair_profit': pair_profit_by_momth,
            'profit': profit_by_momth,
            'total': pair_profit_by_momth + profit_by_momth
        })
        year_profits['pair_profit'] += pair_profit_by_momth
        year_profits['profit'] += profit_by_momth
        year_profits['total'] += pair_profit_by_momth + profit_by_momth
        month -= 1

    aggregates_by_months.append(year_profits)
    recent_transactions = account.recent_transactions()

    all_time_profits = {}
    all_time_profits['pair_finished']= all_account_pair_transactions.aggregate(profit=Sum('profit'))['profit'] or 0
    all_time_profits['pair_unfinished'] = sum([pt.get_profit() for pt in all_account_pair_transactions.filter(finished__isnull=True)])
    all_time_profits['bs_finished']= all_account_bs_transactions.aggregate(profit=Sum('profit'))['profit'] or 0
    all_time_profits['bs_unfinished']= sum([t.get_profit() for t in all_account_bs_transactions.filter(finished__isnull=True)])
    all_time_profits['pair'] = all_time_profits['pair_finished'] + all_time_profits['pair_unfinished']
    all_time_profits['bs'] = all_time_profits['bs_finished'] + all_time_profits['bs_unfinished']
    all_time_profits['total'] = all_time_profits['bs'] + all_time_profits['pair']

    context = {
        'account': account,
        'get_price_job': get_price_job,
        'snapshots': snapshots,
        'snapshots_chart_data': snapshots_chart_data,
        'logged_in': logged_in,
        'star_stocks': star_stocks,
        'recent_pair_transactions': recent_pair_transactions,
        'pair_transactions_unfinished': pair_transactions_unfinished,
        'pair_virtual_profit': pair_virtual_profit,
        'account_bs_transactions': account_bs_transactions,
        'bs_transactions_this_month': bs_transactions_this_month,
        'bs_transactions_unfinished': bs_transactions_unfinished,
        'transaction_profit': transaction_profit,
        'transaction_virtual_profit': transaction_virtual_profit,
        'aggregates_by_months': aggregates_by_months,
        'year_profits': year_profits,
        'recent_transactions': recent_transactions,
        'all_time_profits': all_time_profits,
    }
    context.update(get_pairs_context(request))
    return render(request, 'stocks/account_details.html', context)


def get_pairs_context(request):
    star_pairs = StockPair.objects.filter(star=True)
    ids = star_pairs.values_list('target_stock', 'started_stock')
    stock_ids = []
    for i in ids:
        stock_ids.extend(i)
    stock_ids = set(stock_ids)

    pair_stocks = Stock.objects.filter(id__in=stock_ids)
    if request.GET.get('force_update', False):
        update_stocks_prices(pair_stocks)

    return {"pairs": star_pairs, "update_stocks_prices_url": update_stocks_prices_url(pair_stocks)}


@staff_member_required
def pair_list(request):
    context = get_pairs_context(request)
    return render(request, 'stocks/includes/pair_list.html', context)


@staff_member_required
def pair_details(request, pair_id):
    pair = StockPair.objects.get(id=pair_id)
    pair_transactions = PairTransaction.objects.all().filter(pair=pair).\
        filter(finished__isnull=False).order_by('-finished')
    unfinished_pair_transactions = PairTransaction.objects.all().\
        filter(pair=pair).exclude(finished__isnull=False).order_by('-started')

    context = {
        'pair': pair,
        'pair_transactions': pair_transactions,
        'unfinished_pair_transactions': unfinished_pair_transactions,
    }
    return render(request, 'stocks/pair_details.html', context)


def account_snapshot(request, account_slug, snapshot_number):
    logged_in = request.user.is_authenticated()
    account = Account.objects.get(slug=account_slug)
    if not account.public and not request.user.is_authenticated():
        return HttpResponseForbidden('Oops')
    snapshot = account.snapshots.all().get(serial_number=snapshot_number)
    transactions = snapshot.find_transactions()
    context = {
        'account': account,
        'snapshot': snapshot,
        'logged_in': logged_in,
        'transactions': transactions,
    }
    context.update(get_pairs_context(request))
    return render(request, 'stocks/account_snapshot.html', context)
