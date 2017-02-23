from django.core.management import call_command


def poll_feeds():
    call_command('poll_feeds')

cron_jobs = [
    dict(
        cron_string='0 * * * *',                # A cron string (e.g. "0 0 * * 0")
        func=poll_feeds,                  # Function to be queued
        args=[],          # Arguments passed into function when executed
        kwargs={},      # Keyword arguments passed into function when executed
        repeat=None,                   # Repeat this number of times (None means repeat forever)
        queue_name='default'       # In which queue the job should be put in
    ),
]


