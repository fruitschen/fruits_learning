# -*- coding: UTF-8 -*-


from django.apps import AppConfig
from django.core.checks import Error, register
from django.db.utils import OperationalError
from decimal import Decimal


@register()
def snapshots_check(app_configs, **kwargs):
    """自动检查过去snapshots的净值。必须确保代码修改不会不小心造成账户净值出错。"""
    from stocks.models import Account, Snapshot
    errors = []
    try:
        public_account = Account.objects.get(id=4)

        snapshots = public_account.snapshots.all()[:13]
        expected_net_assets = [
            Decimal('402409.11'), Decimal('418005.48'), Decimal('448114.82'), Decimal('460585.62'),
            Decimal('532143.95'), Decimal('513612.32'), Decimal('545341.27'), Decimal('568601.91'),
            Decimal('591513.78'), Decimal('581557.38'), Decimal('600266.95'), Decimal('710184.95'),
            Decimal('760989.55')
        ]
        expected_increases = [
            Decimal('0.0000'), Decimal('0.0388'), Decimal('0.0720'), Decimal('0.0278'), Decimal('0.1554'),
            Decimal('-0.0348'), Decimal('0.0618'), Decimal('0.0427'), Decimal('0.0403'), Decimal('-0.0168'),
            Decimal('0.0322'), Decimal('0.1831'),
            Decimal('0.0715')
        ]
        for i, snapshot in enumerate(snapshots):
            if i+1 != snapshot.serial_number:
                errors.append(
                    Error(
                        'serial number error',
                        hint='{} != {}'.format(snapshot.serial_number, i+1),
                        obj=Snapshot,
                        id='stocks.E001',
                    )
                )

            if (snapshot.serial_number - 1) % 12 == 0:
                if not snapshot.is_annual:
                    errors.append(
                        Error(
                            'is_annual',
                            hint='is_annual_should be True for snapshot {}'.format(snapshot.serial_number),
                            obj=Snapshot,
                            id='stocks.E002',
                        )
                    )

            expected_net_asset = expected_net_assets[i]
            if snapshot.net_asset != expected_net_asset:
                errors.append(
                    Error(
                        'Net asset mismatch',
                        hint='Net asset should be {} for snapshot #{}. Yet it is {}'.format(expected_net_asset,
                                                                                            snapshot.serial_number,
                                                                                            snapshot.net_asset),
                        obj=Snapshot,
                        id='stocks.E003',
                    )
                )

            expected_increase = expected_increases[i]
            if snapshot.increase != expected_increase:
                errors.append(
                    Error(
                        'Change mismatch',
                        hint='Change should be {} for snapshot #{}. Yet it is {}'.format(expected_increase,
                                                                                            snapshot.serial_number,
                                                                                            snapshot.increase),
                        obj=Snapshot,
                        id='stocks.E004',
                    )
                )
        return errors
    except (OperationalError, Account.DoesNotExist):
        return []  # skip if database is not created/migrated yet, or account doesn't exit.


class StocksConfig(AppConfig):
    name = 'stocks'

    def ready(self):
        pass
