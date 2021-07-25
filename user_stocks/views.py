# -*- coding: UTF-8 -*-
import functools
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseForbidden

from user_stocks.models import *
from stocks.jobs import get_price


def stocks(request):
    logged_in = request.user.is_authenticated
    user = request.user
    if user.is_staff:
        accounts = UserAccount.objects.all()
    elif logged_in:
        accounts = UserAccount.objects.filter(user=user)
    context = {
        'accounts': accounts,
    }
    return render(request, 'user_stocks/user_stocks.html', context)


def account_details(request, account_slug):
    logged_in = request.user.is_authenticated
    get_price_job = None
    if logged_in and request.GET.get('update', False):
        get_price_job = get_price.delay()
    account = UserAccount.objects.get(slug=account_slug)
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Oops')
    snapshots = account.snapshots.all().order_by('-id')
    snapshots_chart_data = None
    if snapshots.count() >= 3:
        raw_data = snapshots.values_list('date', 'net_asset')
        raw_data = raw_data.reverse()
        dates = [r[0] for r in raw_data]
        x_axis = [r[0].strftime('%Y-%m-%d') for r in raw_data]
        y_axis = [int(r[1]) for r in raw_data]
        snapshots_chart_data = {'x_axis': x_axis, 'y_axis': y_axis}
    
    now = timezone.now()
    
    def cmp_func(x, y):
        return int(y.total - x.total)
    
    account_stocks = sorted(account.stocks.filter(amount__gt=0), key=functools.cmp_to_key(cmp_func))

    context = {
        'account': account,
        'get_price_job': get_price_job,
        'snapshots': snapshots,
        'snapshots_chart_data': snapshots_chart_data,
        'logged_in': logged_in,
        'is_admin': logged_in and request.user.is_staff or request.user == account.user,
        'account_stocks': account_stocks,
    }
    return render(request, 'user_stocks/user_account_details.html', context)


@staff_member_required
def take_snapshot(request, account_slug):
    if request.method == 'POST':
        account = UserAccount.objects.get(slug=account_slug)
        account.take_snapshot()
    return redirect('user_account_details', account_slug=account_slug)


def account_snapshot(request, account_slug, snapshot_number):
    logged_in = request.user.is_authenticated
    account = UserAccount.objects.get(slug=account_slug)
    if not request.user.is_staff and request.user != account.user:
        return HttpResponseForbidden('Oops')
    snapshot = account.snapshots.all().get(serial_number=snapshot_number)
    snapshots = account.snapshots.all().order_by('-id')
    context = {
        'account': account,
        'snapshot': snapshot,
        'snapshots': snapshots,
        'logged_in': logged_in,
        'snapshot_stocks': snapshot.stocks_ordered,
    }
    if snapshot.is_annual:
        first_snapshot_this_year = snapshot.serial_number - 12
        incs = account.snapshots.filter(
            serial_number__lte=snapshot.serial_number, serial_number__gte=first_snapshot_this_year
        ).values_list('increase', flat=True)
        max_inc = max(incs) * 100
        min_inc = min(incs) * 100
        context.update({
            'max_inc': max_inc,
            'min_inc': min_inc,
        })
    return render(request, 'user_stocks/user_account_snapshot.html', context)
