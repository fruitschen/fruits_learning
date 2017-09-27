from django.apps import AppConfig
from django.conf import settings
from .jobs import cron_jobs
import django_rq
scheduler = django_rq.get_scheduler('default')


class HomeConfig(AppConfig):
    name = 'home'
    verbose_name = 'Home'

    def ready(self):
        # if jobs are disabled for this setup
        if getattr(settings, 'DISABLE_ALL_JOBS', False):
            return
        scheduled_jobs = scheduler.get_jobs()
        for cron_job in cron_jobs:
            job_already_queued = False
            for job in scheduled_jobs:
                if job.func == cron_job['func'] \
                        and job.meta.get('cron_string', '') == cron_job['cron_string'] \
                        and job.args == cron_job['args'] \
                        and job.args == cron_job['args']:
                    job_already_queued = True
                    break
            if not job_already_queued:
                scheduler.cron(**cron_job)
