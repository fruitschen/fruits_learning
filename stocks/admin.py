# -*- coding: UTF-8 -*-
from django.contrib import admin

from stocks.models import (Stock, StockPair, PairTransaction, Transaction, Account,
                           AccountStock, Snapshot, SnapshotStock)


def add_star(modeladmin, request, queryset):
    queryset.update(star=True)
add_star.short_description = "Star"


def remove_star(modeladmin, request, queryset):
    queryset.update(star=True)
remove_star.short_description = "Unstar"


class StockAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'price', 'market', 'star' ]
    list_filter = ['star', ]
    search_fields = ['name', 'code',]
    actions = [add_star, remove_star, ]


class PairTransactionAdmin(admin.ModelAdmin):
    list_display = ['sold_stock', 'bought_stock', 'profit', 'started', 'finished']
    list_filter = ['finished', ]
    readonly_fields = ['profit', ]


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['bought_stock', 'bought_price', 'profit', 'started', 'finished']
    list_filter = ['finished', ]
    readonly_fields = ['profit', ]


class PairAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'current_value', ]
    list_filter = ['star', ]
    actions = [add_star]


class AccountStockInline(admin.TabularInline):
    model = AccountStock


class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'public', ]
    inlines = [AccountStockInline]


class SnapshotStockInline(admin.TabularInline):
    model = SnapshotStock


class SnapshotAdmin(admin.ModelAdmin):
    model = Snapshot
    inlines = [SnapshotStockInline]

admin.site.register(Stock, StockAdmin)
admin.site.register(StockPair, PairAdmin)
admin.site.register(PairTransaction, PairTransactionAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Snapshot, SnapshotAdmin)
