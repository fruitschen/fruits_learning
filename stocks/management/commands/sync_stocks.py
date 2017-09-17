# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = u'将本地的stocks数据同步到服务器'

    def handle(self, *args, **options):
        yes = raw_input('确定要把本地的stocks数据同步到服务器y/n?\n')
        if yes != 'y':
            print 'Quit.'
            return

        commands = settings.SYNCS['sync_stocks_to_server']
        for cmd in commands:
            print cmd
            os.system(cmd)