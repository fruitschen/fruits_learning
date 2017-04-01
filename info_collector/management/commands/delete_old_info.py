"""
This command mark the old info as deleted.
"""
from __future__ import absolute_import

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from ...models import Info

import logging

logger = logging.getLogger('info_collector')

class Command(BaseCommand):
    args = 'none'
    help = 'Mark old info as deleted.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='Print progress on command line'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        seven_days_ago = timezone.now() - timedelta(days=7)
        old_items = Info.objects.filter(is_deleted=False, starred=False, is_read=True, timestamp__lt=seven_days_ago)
        if verbose:
            print('%d potential items' % (old_items.count()))
        old_items.update(is_deleted=True)

        logger.info('Info delete_old_info completed successfully')
