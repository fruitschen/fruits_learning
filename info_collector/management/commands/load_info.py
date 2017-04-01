"""
This command load info from a json file produced by sync_info
"""
from __future__ import absolute_import
import os

from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from ...models import Info, Author

import logging

logger = logging.getLogger('info_collector')

class Command(BaseCommand):
    args = 'none'
    help = 'load info'

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')

        author_data = open(os.path.join(settings.INFO_SYNC['LOAD_FROM'], 'author.json'), 'r').read()
        authors = serializers.deserialize(
            "json", author_data, indent=2, use_natural_foreign_keys=True, use_natural_primary_keys=True
        )
        for author in authors:
            author.save()

        info_data = open(os.path.join(settings.INFO_SYNC['LOAD_FROM'], 'info.json'), 'r').read()
        info_items = serializers.deserialize(
            "json", info_data, indent=2, use_natural_foreign_keys=True, use_natural_primary_keys=True
        )
        for info in info_items:
            info.save()

        if verbosity:
            print('import done')

        logger.info('sync_info completed successfully')
