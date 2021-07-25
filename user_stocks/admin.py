from django.contrib import admin

from user_stocks.models import (
    UserAccount,
    UserAccountSnapshot,
    UserAccountSnapshotStock,
    UserAccountStock
)


class UserAccountStockInline(admin.TabularInline):
    model = UserAccountStock
    autocomplete_fields = ['stock']


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', ]
    inlines = [UserAccountStockInline, ]


class UserSnapshotStockInline(admin.TabularInline):
    model = UserAccountSnapshotStock
    autocomplete_fields = ['stock']


@admin.register(UserAccountSnapshot)
class UserAccountSnapshotAdmin(admin.ModelAdmin):
    model = UserAccountSnapshot
    inlines = [UserSnapshotStockInline]
    list_display = ['account', 'serial_number', 'date', 'increase']
    list_filter = ['account', ]


