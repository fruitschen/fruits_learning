# coding: utf-8

TAGS = [
    '业绩快报',
    '业绩预增',
    '业绩预告',
    '利润分配实施',
    '派息实施',
    '权益分派实施',
    '分红派息',
    '对外投资',
    '复牌',
    '非公开发行股票',
    '发行股份购买资产',
    '补贴',
    '减持',
    '增持',
    '激励',

    '警示函',
    '问询函',
    '销售情况',
    '自愿',
]

def apply_tags(info):
    needs_save = False
    for tag in TAGS:
        if tag in info.title and not tag in info.tags:
            if info.tags:
                info.tags += tag
            else:
                info.tags = tag
            needs_save = True
    if needs_save:
        info.save()
