# coding: utf-8
from django.shortcuts import render

from decimal import Decimal
from stocks.templatetags.money import money_display

def compound_interest(request):
    cols = [8, 10, 15, 20, 25, 30]
    years = range(1, 51)
    rows = []
    base = 1
    if request.GET.get('base', False):
        base = Decimal(request.GET.get('base'))
    skip = None
    if request.GET.get('skip'):
        skip = int(request.GET.get('skip'))

    for year in years:
        if skip and year > skip:
            if year % skip != 0:
                continue
        row = {
            'title': u'{}年'.format(year),
            'result': [],
        }
        for rate in cols:
             res = (1 + Decimal(rate)/Decimal('100')) ** year * base
             earning = (res - 1)
             earning_percent = earning * 100
             if base != 1:
                 display = money_display(res)
                 display = '{}万'.format('%.2f' % (res / 10000))
             elif earning > 1:
                 display = u'{}倍'.format('%.2f' % earning)
             else:
                 display = u'{}%'.format('%.2f' % earning_percent)
             row['result'].append(display)
        rows.append(row)
    context = {
        'cols': cols,
        'rows': rows,
    }
    return render(request, 'compound_interest.html', context)


def fund_value_estimation(request):
    fund_price = Decimal('0.62')
    fund_value = Decimal('0.646')
    fee = (Decimal('1') + Decimal('0.22')) / 100
    interest_rate = Decimal('7.25') / 100

    initial_fund_value = Decimal('0.65')  # 净值为0.65时候初始估值大概是1
    initial_pb = 1
    initial_leverage = leverage = (1 + fund_value) / fund_value
    groups = [
        {'roe': Decimal('15'), },
        {'roe': Decimal('10'), },
        {'roe': Decimal('18'), },
        {'roe': Decimal('5'), },
        {'roe': Decimal('20'), },
    ]
    for group in groups:
        results = []
        fund_value = Decimal('0.65')
        fund_values = []
        roe = group['roe'] / 100
        while fund_value <= Decimal('1.6'):
            fund_values.append(fund_value)
            inc = (fund_value / initial_fund_value) - 1
            pb_inc = inc / initial_leverage
            pb = initial_pb + pb_inc
            money = 1 + fund_value  # 动用的资金
            asset = money / pb
            leverage = money / fund_value
            profit = asset * roe
            total_fee = money * fee
            interest = interest_rate * 1
            real_profit = profit - total_fee - interest
            fund_pe = fund_value / real_profit
            fund_roe = real_profit / fund_value * 100

            result = {
                'fund_value': fund_value,
                'pb': pb,
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
            results.append(result)
            fund_value += Decimal('0.1')
        group['results'] = results

    context = {
        'groups': groups,
    }
    return render(request, 'fund_value_estimation.html', context)
