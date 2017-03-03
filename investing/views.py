# coding: utf-8
from django.shortcuts import render

from decimal import Decimal


def fund_value_estimation(request):
    roe = Decimal('15') / 100
    fund_price = Decimal('0.62')
    pb = 1
    fund_value = Decimal('0.646')
    fee = (Decimal('1') + Decimal('0.22')) / 100
    interest_rate = Decimal('7.25') / 100

    money = 1 + fund_value  # 动用的资金
    asset = money / pb
    leverage = money / fund_value
    profit = asset * roe
    total_fee = money * fee
    interest = interest_rate * 1
    real_profit = profit - total_fee - interest
    fund_pe = fund_value / real_profit
    fund_roe = real_profit / fund_value * 100

    context = {
        'fund_value': fund_value,
        'leverage': leverage,
        'money': money,
        'asset': asset,
        'profit': profit,
        'total_fee': total_fee,
        'interest': interest,
        'real_profit': real_profit,
        'fund_pe': fund_pe,
        'fund_roe': fund_roe,
    }
    return render(request, 'fund_value_estimation.html', context)

