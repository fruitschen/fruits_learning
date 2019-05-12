# -*- coding: UTF-8 -*-
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from home.utils import get_current_country


def poll_feeds():
    call_command('poll_feeds')


def delete_old_info():
    call_command('delete_old_info')


def run_backup():
    """backup database with django-backup"""
    call_command('backup', compress=True, cleanlocaldb=True)


def run_crawlers():
    # 服务器上暂时不运行info crawlers
    if not settings.RUN_INFO_CRAWLERS:
        return
    # IP不对，暂时不运行
    # TODO: Display a notification at least
    try:
        country = get_current_country()
        if country != 'China':
            return
    except:
        pass
    from info_collector import crawlers
    info_crawlers = (
        crawlers.TechQQCrawler(),
        crawlers.XueqiuHomeCrawler(),
        crawlers.XueqiuPeopleCrawler(),
        crawlers.StocksCrawler(),
        # crawlers.StocksAnnouncementCrawler(),
    )
    for crawler in info_crawlers:
        if crawler.info_source.should_fetch():
            crawler.run()


def auto_update_price():
    now = timezone.now()
    trading_days = [0, 1, 2, 3, 4]
    # 9:15开始，每小时更新一次价格，15:15之后停止更新。
    trading_start = timezone.datetime(now.year, now.month, now.day, 9, 15, tzinfo=timezone.get_current_timezone())
    trading_end = timezone.datetime(now.year, now.month, now.day, 15, 15, tzinfo=timezone.get_current_timezone())
    if now.weekday() in trading_days and trading_start < now < trading_end:
        call_command('get_price')


def pull_server_backups():
    SYNCS = getattr(settings, 'SYNCS', None)
    if SYNCS and SYNCS.get('pull_server_backups', False):
        cmd = SYNCS.get('pull_server_backups', False)
        if cmd:
            import os
            os.system(cmd)


def sync_info():
    SYNCS = getattr(settings, 'SYNCS', None)
    if SYNCS and SYNCS.get('enable_push_info_items', False):
        call_command('sync_info')


def pull_recent_read_info_items():
    """定期从服务器下载已读的info"""
    SYNCS = getattr(settings, 'SYNCS', None)
    if SYNCS and SYNCS.get('enable_pull_recent_read_info_items', False):
        from info_collector.models import SyncLog, Info
        from diary.models import DATE_FORMAT
        from info_collector.views import ReadInfoSerializer
        import requests
        start_date_str = '2017-09-01'
        if SyncLog.objects.filter(action='server_to_local').exists():
            last_sync_time = SyncLog.objects.filter(action='server_to_local')[0].timestamp
            start_date_str = (last_sync_time - timedelta(days=1)).strftime(DATE_FORMAT)
        url = 'http://www.fruitschen.com/info/reader/recent_read_items/?start_date={}'.format(start_date_str)
        response = requests.get(url)
        serializer = ReadInfoSerializer(data=response.json(), many=True)
        if serializer.is_valid():
            for read_info in serializer.validated_data:
                info_item = Info.objects.get(id=read_info['id'])
                if not info_item.is_read:
                    if read_info['read_at']:
                        info_item.is_read = True
                        info_item.read_at = read_info['read_at']
                    if read_info['starred_at']:
                        info_item.starred_at = read_info['starred_at']
                        info_item.starred = True
                    info_item.save()
            SyncLog.objects.create(action='server_to_local')
        else:
            raise RuntimeError('Info Collector failed to sync from server. ')


cron_jobs = [
    dict(
        cron_string='0 * * * *',                # An hourly job
        func=poll_feeds,                  # Function to be queued
        args=[],          # Arguments passed into function when executed
        kwargs={},      # Keyword arguments passed into function when executed
        repeat=None,                   # Repeat this number of times (None means repeat forever)
        queue_name='default'       # In which queue the job should be put in
    ),
    dict(
        cron_string='*/5 * * * *',  # A cron string (e.g. "0 0 * * 0")
        func=run_crawlers,
        args=[],
        kwargs={},
        repeat=None,  # Repeat forever
        queue_name='default'
    ),
    dict(
        cron_string='1 * * * *',
        func=delete_old_info,
        args=[],
        kwargs={},
        repeat=None,
        queue_name='default'
    ),
    dict(
        cron_string='5 * * * *',
        func=auto_update_price,
        args=[],
        kwargs={},
        repeat=None,
        queue_name='default'
    ),
    dict(
        cron_string='0 11 * * *',
        func=run_backup,
        args=[],
        kwargs={},
        repeat=None,
        queue_name='default'
    ),
    dict(
        cron_string='20 * * * *',
        func=pull_server_backups,
        args=[],
        kwargs={},
        repeat=None,
        queue_name='default'
    ),
    dict(
        cron_string='10 */2 * * *',
        func=sync_info,
        args=[],
        kwargs={},
        repeat=None,
        queue_name='default'
    ),
]
