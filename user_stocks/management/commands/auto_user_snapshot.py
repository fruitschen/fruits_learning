# -*- coding: UTF-8 -*-
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

from user_stocks.models import UserAccount


class Command(BaseCommand):
    help = '每天自动创建用户账户的快照'

    def handle(self, *args, **options):
        now = datetime.now()
        today = timezone.datetime(now.year, now.month, now.day, 15, 0, 0, tzinfo=timezone.get_current_timezone())
        if now.hour > 15:
            user_accounts = UserAccount.objects.all()
            for user_account in user_accounts:
                if not user_account.snapshots.filter(date__gte=today):
                    call_command('get_price')
                    user_account.take_snapshot()
