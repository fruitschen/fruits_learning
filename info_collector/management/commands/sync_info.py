"""
This command sync the info data between desktop and server
"""

import os

from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from ...models import Info, Author, SyncLog, Content
from reads.models import Read
from home.jobs import pull_recent_read_info_items

import logging

logger = logging.getLogger('info_collector')


class Command(BaseCommand):
    args = 'none'
    help = 'sync the info data between desktop and server.'

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')

        if verbosity:
            print('Pulling read info items.')
        pull_recent_read_info_items()
        if verbosity:
            print('Done pulling read info items.')

        authors = Author.objects.all()
        author_data = serializers.serialize(
            "json", authors, indent=2
        )
        open(os.path.join(settings.INFO_SYNC['DUMP_TO'], 'author.json'), 'w').write(author_data)

        a_week_ago = timezone.now() - timedelta(days=7)
        start = a_week_ago
        if SyncLog.objects.filter(action='local_to_server').exists():
            last_sync_time = SyncLog.objects.filter(action='local_to_server')[0].timestamp
            start = last_sync_time - timedelta(days=1)
        recent_items = Info.objects.filter(Q(timestamp__gt=start) | Q(read_at__gte=start))
        recent_contents = Content.objects.filter(info__in=recent_items)

        if verbosity:
            print(('exporting %d items' % (recent_items.count())))
        fields = [f.name for f in Info._meta.fields]
        data = serializers.serialize(
            "json", recent_items, indent=2, fields=fields
        )
        content_fields = [f.name for f in Content._meta.fields]
        content_data = serializers.serialize(
            "json", recent_contents, indent=2, fields=content_fields
        )
        open(os.path.join(settings.INFO_SYNC['DUMP_TO'], 'content.json'), 'w').write(content_data)
        open(os.path.join(settings.INFO_SYNC['DUMP_TO'], 'info.json'), 'w').write(data)

        reads_items = Read.objects.all()
        if verbosity:
            print(('exporting %d items' % (reads_items.count())))
        fields = [f.name for f in Read._meta.fields]
        data = serializers.serialize(
            "json", reads_items, indent=2, fields=fields
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

        SyncLog.objects.create(action='local_to_server')
