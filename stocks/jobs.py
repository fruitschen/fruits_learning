from django.core.management import call_command
from django_rq import job

@job
def get_price():
    call_command('get_price')


