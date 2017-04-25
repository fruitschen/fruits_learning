"""
This command sync the info data between desktop and server
"""
from __future__ import absolute_import
import os

from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from ...models import Info, Author
from reads.models import Read

import logging

logger = logging.getLogger('info_collector')

class Command(BaseCommand):
    args = 'none'
    help = 'sync the info data between desktop and server.'

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')

        authors = Author.objects.all()
        author_data = serializers.serialize(
            "json", authors, indent=2, use_natural_foreign_keys=True, use_natural_primary_keys=True
        )
        open(os.path.join(settings.INFO_SYNC['DUMP_TO'], 'author.json'), 'w').write(author_data)

        two_weeks_ago = timezone.now() - timedelta(days=14)
        recent_items = Info.objects.filter(timestamp__gt=two_weeks_ago)
        if verbosity:
            print('exporting %d items' % (recent_items.count()))
        fields = [f.name for f in Info._meta.fields]
        fields = filter(lambda x: x not in ['id', 'content'], fields)
        data = serializers.serialize(
            "json", recent_items, indent=2, fields=fields, use_natural_foreign_keys=True, use_natural_primary_keys=True
        )
        open(os.path.join(settings.INFO_SYNC['DUMP_TO'], 'info.json'), 'w').write(data)

        reads_items = Read.objects.all()
        if verbosity:
            print('exporting %d items' % (reads_items.count()))
        fields = [f.name for f in Read._meta.fields]
        fields = filter(lambda x: x not in ['id', ], fields)
        data = serializers.serialize(
            "json", reads_items, indent=2, fields=fields, use_natural_foreign_keys=True
        )
        open(os.path.join(settings.INFO_SYNC['DUMP_TO'], 'reads.json'), 'w').write(data)


        cmd = 'rsync -rave ssh {} {}:{}'.format(
            settings.INFO_SYNC['DUMP_TO'], settings.INFO_SYNC['SERVER'], settings.INFO_SYNC['LOAD_FROM']
        )
        if verbosity:
            print(cmd)
        ret = os.system(cmd)

        cmd = 'ssh {} "{}"'.format(
            settings.INFO_SYNC['SERVER'], settings.INFO_SYNC['LOAD_CMD']
        )
        if verbosity:
            print(cmd)
        ret = os.system(cmd)
        logger.info('sync_info completed successfully')
