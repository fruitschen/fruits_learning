# -*- coding: UTF-8 -*-
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

def poll_feeds():
    call_command('poll_feeds')


def delete_old_info():
    call_command('delete_old_info')


def run_backup():
    """backup database with django-backup"""
    call_command('backup', compress=True, cleanlocaldb=True)


def run_crawlers():
    from info_collector import crawlers
    info_crawlers = (
        crawlers.TechQQCrawler(),
        crawlers.XueqiuHomeCrawler(),
        crawlers.DoubanBookCrawler(),
        crawlers.XueqiuPeopleCrawler(),
        crawlers.StocksCrawler(),
        crawlers.StocksAnnouncementCrawler(),
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
]
