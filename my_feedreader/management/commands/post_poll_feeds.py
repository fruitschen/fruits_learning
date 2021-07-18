

from django.core.management.base import BaseCommand
from django.utils import timezone

from info_collector.models import InfoSource, Author, Info, Content
from feedreader.models import Feed, Entry

import logging

logger = logging.getLogger('feedreader')


def get_or_create_RSS_info_source():
    info_source, created = InfoSource.objects.get_or_create(
        slug='rss',
        defaults=dict(
            name='RSS',
            url='http://www.fruitschen.com/',
            interval=3600 * 24,
            description='Info from feed_reader app'
        )
    )
    return info_source


def get_author_for_feed(feed):
    author, created = Author.objects.get_or_create(
        url=feed.link,
        defaults=dict(
            name=feed.title,
            raw='\n'.join([feed.xml_url, feed.description]),
        )
    )
    return author

    
class Command(BaseCommand):
    args = 'none'
    help = 'After poll_feeds, we convert the Entries into Info.'

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
        """
        Read through all the feeds, and convert entries into info items.
        """
        verbose = options['verbose']
        total_unread_untries = Entry.objects.filter(read_flag=False)
        if not total_unread_untries.count():
            if verbose:
                print('Nothing to convert. ')
            return
        
        rss_info_source = get_or_create_RSS_info_source()
        feeds = Feed.objects.all()
        for feed in feeds:
            author = get_author_for_feed(feed)
            unread_untries = Entry.objects.filter(read_flag=False, feed=feed)
            num_entries = len(unread_untries)
            if verbose:
                print(('%s %d entries to process' % (feed, num_entries)))
            for entry in unread_untries:
                Info.objects.create(
                    info_source=rss_info_source,
                    title=entry.title,
                    author=author,
                    identifier=entry.link,
                    url=entry.link,
                    content=Content.objects.create(content=entry.description),
                    status=Info.NEW,
                    important=True,
                    original_timestamp=entry.published_time,
                )
                entry.read_flag=True
                entry.save()
        rss_info_source.last_fetched = timezone.now()
        rss_info_source.save()
