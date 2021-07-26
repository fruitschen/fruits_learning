from decimal import Decimal
from datetime import timedelta, datetime
from django.db import models
from django.urls import reverse
from stocks.models import BaseAccount, BaseAccountStock, BaseSnapshot, BaseSnapshotStock


class UserAccount(BaseAccount):
    user = models.ForeignKey('auth.User', verbose_name='用户', on_delete=models.PROTECT)
    
    @property
    def net(self):
        return self.total

    @property
    def total(self):
        """股票、子账户、现金合计"""
        return self.stocks_total + self.cash

    def take_snapshot(self):
        """制作一个账户快照 quick account snapshot"""
        if self.snapshots.all():
            serial_number = 1 + self.snapshots.all().order_by('-serial_number')[0].serial_number
        else:
            serial_number = 1
        snapshot = UserAccountSnapshot(
            account=self,
            date=datetime.today(),
            serial_number=serial_number,
            stocks_asset=self.stocks_total,
            net_asset=self.net,
            cash=self.cash,
        )
        snapshot.save()
        snapshot = UserAccountSnapshot.objects.get(id=snapshot.id)
        for account_stock in self.stocks.all():
            stock = account_stock.stock
            UserAccountSnapshotStock.objects.create(
                snapshot=snapshot,
                stock=stock,
                amount=account_stock.amount,
                price=stock.price,
                name=stock.name,
                code=stock.code,
                total=account_stock.total
            )
        snapshot.calculate_net_asset()
        snapshot.save()

    def get_absolute_url(self):
        return reverse('user_account_details', args=(self.slug,))
    
    class Meta:
        verbose_name = '账户'
        verbose_name_plural = verbose_name
        

class UserAccountStock(BaseAccountStock):
    """账户当前持有的股票"""
    stock = models.ForeignKey('stocks.Stock', verbose_name='股票', on_delete=models.PROTECT)
    amount = models.PositiveIntegerField(verbose_name='数量')
    account = models.ForeignKey('UserAccount', verbose_name='账户', related_name='stocks', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '账户股票'
        verbose_name_plural = verbose_name


class UserAccountSnapshot(BaseSnapshot):
    """账户快照，保存一个账户在某个时间点的净资产，持有股票等等"""

    sub_accounts_asset = 0
    account = models.ForeignKey('UserAccount', verbose_name='账户', related_name='snapshots', on_delete=models.PROTECT)

    @property
    def transactions_count(self):
        return 0

    @property
    def debt(self):
        return 0

    class Meta:
        verbose_name = '账户快照'
        verbose_name_plural = verbose_name


class UserAccountSnapshotStock(BaseSnapshotStock):
    """账户快照 当时持有的股票"""
    snapshot = models.ForeignKey('UserAccountSnapshot', related_name='stocks', verbose_name='快照',
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = '账户快照股票'
        verbose_name_plural = verbose_name

