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


def fund_value_estimation(request, code='150292'):
    funds = [
        {
            # (某时间点)，净值为0.65时候初始估值大概是1
            # 2019年末, 净值为0.85时候初始估值大概是0.8
            # 懒得计算PB
            'code': '150292',
            'name': u'银行B份',
            'fund_value': Decimal('0.85'),
            'initial_pb': Decimal('0.85'),
            'fee': (Decimal('1') + Decimal('0.22')) / 100,
            'interest_rate': (Decimal('4') + Decimal('1.5')) / 100,
            'roe_list': [12, 15, 10, 18, 5, 20],
        },
        {
            'code': '150118',
            'name': u'房地产B',
            'fund_value': Decimal('1.15'),
            'initial_pb': Decimal('1.5'),
            'fee': (Decimal('1') + Decimal('0.2')) / 100,
            'interest_rate': (Decimal('4') + Decimal('1.5')) / 100,
            'roe_list': [18, 15, 20, 25],
        },
        {
            'code': '150228',
            'name': u'银行B',
            'fund_value': Decimal('0.95'),
            'initial_pb': Decimal('0.85'),
            'fee': (Decimal('1') + Decimal('0.22')) / 100,
            'interest_rate': (Decimal('3') + Decimal('1.5')) / 100,
            'roe_list': [12, 15, 10, 18, 5, 20],
        },
    ]
    for fund in funds:
        if fund['code'] == code:
            break
    fund_value = fund['fund_value']
    fee = fund['fee']
    interest_rate = fund['interest_rate']
    initial_fund_value = fund_value
    initial_pb = fund['initial_pb']
    initial_leverage = leverage = (1 + fund_value) / fund_value
    
    groups = [
        {'roe': Decimal(roe), } for roe in fund['roe_list']
    ]
    calc_limit = fund_value * 2
    for group in groups:
        results = []
        fund_value = fund['fund_value']
        fund_values = []
        roe = group['roe'] / 100
        while fund_value <= calc_limit:
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
            parent_fund_pe = Decimal(1 / (1 / pb * roe))
            fund_pe = fund_value / real_profit
            fund_roe = real_profit / fund_value * 100
            
            years = []
            max_year = int(request.GET.get('max_year', 0))
            asset_next_year = asset * (1 + real_profit)
            for year in range(1, max_year+1):
                profit_next_year = asset_next_year * roe
                real_profit_next_year = profit_next_year - total_fee - interest
                asset_next_year = asset_next_year + real_profit_next_year
                fund_pe_next_year = fund_value / real_profit_next_year
                fund_roe_next_year = real_profit_next_year / fund_value * 100
                years.append({'year': year, 'roe': fund_roe_next_year, 'pe': fund_pe_next_year})
                
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
                'parent_fund_pe': parent_fund_pe,
                'fund_roe': fund_roe,
                'years': years,
            }
            results.append(result)
            fund_value += Decimal('0.1')
        group['results'] = results

    context = {
        'groups': groups,
        'fund': fund,
        'funds': funds,
    }
    return render(request, 'fund_value_estimation.html', context)
