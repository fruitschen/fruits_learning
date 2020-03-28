# -*- coding: UTF-8 -*-
from django.contrib import admin

from stocks.models import (Stock, StockPair, PairTransaction, BoughtSoldTransaction, Account, SubAccount,
                           AccountStock, Snapshot, SnapshotStock, Transaction, AccountStocksRange)
from markdownx.admin import MarkdownxModelAdmin


def add_star(modeladmin, request, queryset):
    queryset.update(star=True)


add_star.short_description = "Star"


def remove_star(modeladmin, request, queryset):
    queryset.update(star=True)


remove_star.short_description = "Unstar"


def combine_pair_transactions(modeladmin, request, queryset):
    base = queryset[0]
    sold_amount = 0
    bought_amount = 0
    sold_total = 0
    bought_total = 0
    for obj in queryset:
        if obj.finished or obj.archived or obj.pair != base.pair or obj.account != base.account\
                or obj.bought_stock != base.bought_stock:
            raise RuntimeError('Cannot combine these pair transactions. ')
        bought_total += obj.bought_total
        sold_total += obj.sold_total
        sold_amount += obj.sold_amount
        bought_amount += obj.bought_amount
    base.bought_price = bought_total / bought_amount
    base.bought_amount = bought_amount
    base.sold_price = sold_total / sold_amount
    base.sold_amount = sold_amount
    base.save()
    for obj in queryset[1:]:
        obj.delete()


combine_pair_transactions.short_description = "Combine"


class StockAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'price', 'market', 'star']
    list_filter = ['star', 'watching']
    search_fields = ['name', 'code', ]
    actions = [add_star, remove_star, ]


class PairTransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'sold_stock', 'bought_stock', 'profit', 'started', 'finished']
    list_filter = ['finished', 'account', 'archived', 'pair']
    readonly_fields = ['profit', ]
    actions = [combine_pair_transactions, ]
    fieldsets = [
        (None, {
            'fields': ('account', 'pair'),
        }),
        (u'正向', {
            'fields': (
                ('sold_stock', 'sold_price', 'sold_amount'),
                ('bought_stock', 'bought_price', 'bought_amount'),
                ('started',),
            )
        }),
        (u'反向', {
            'fields': (
                ('bought_sold_price',),
                ('sold_bought_back_price', 'bought_back_amount', ),
                ('finished',),
            )
        }),
        (u'其它', {
            'fields': (
                ('profit',),
                ('order',),
                ('archived',),
            )
        }),
    ]

class BoughtSoldTransactionAdmin(admin.ModelAdmin):
    list_display = ['bought_stock', 'bought_price', 'profit', 'started', 'finished']
    list_filter = ['finished', 'account', 'archived', ]
    readonly_fields = ['profit', ]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'action', 'stock', 'price', 'amount', 'date', 'has_updated_account', ]
    list_filter = ['account', 'action', 'has_updated_account']


class PairAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'current_value', 'order', 'star']
    list_editable = ['order', ]
    list_filter = ['star', ]
    actions = [add_star]


class AccountStockInline(admin.TabularInline):
    model = AccountStock


class AccountStocksRangeInline(admin.TabularInline):
    model = AccountStocksRange
    extra = 0


class SubAccountInline(admin.TabularInline):
    model = SubAccount


class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'public', ]
    inlines = [AccountStockInline, SubAccountInline, AccountStocksRangeInline]


class SnapshotStockInline(admin.TabularInline):
    model = SnapshotStock


class SnapshotAdmin(MarkdownxModelAdmin):
    model = Snapshot
    inlines = [SnapshotStockInline]
    list_display = ['account', 'serial_number', 'date']
    list_filter = ['account', ]


admin.site.register(Stock, StockAdmin)
admin.site.register(StockPair, PairAdmin)
admin.site.register(PairTransaction, PairTransactionAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(BoughtSoldTransaction, BoughtSoldTransactionAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Snapshot, SnapshotAdmin)
