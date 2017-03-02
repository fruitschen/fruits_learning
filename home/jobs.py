from django.core.management import call_command


def poll_feeds():
    call_command('poll_feeds')


def run_crawlers():
    from info_collector import crawlers
    info_crawlers = (
        crawlers.TechQQCrawler(),
        crawlers.XueqiuHomeCrawler(),
    )
    for crawler in info_crawlers:
        if crawler.info_source.should_fetch():
            crawler.run()


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
]


