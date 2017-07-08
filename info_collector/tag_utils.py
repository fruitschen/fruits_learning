# coding: utf-8

TAGS = [
    u'业绩快报',
    u'业绩预告',
    u'利润分配实施',
    u'派息实施',
    u'权益分派实施',
    u'分红派息',
    u'对外投资',
    u'复牌',
    u'非公开发行股票',
    u'发行股份购买资产',
    u'补贴',
    u'减持',
    u'增持',
    u'激励',

    u'警示函',
    u'问询函',
    u'销售情况',
    u'自愿',
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
