# -*- coding: UTF-8 -*-
from django.core.management import call_command
from django_rq import job


@job
def get_price():
    """异步更新股票价格"""
    call_command('get_price')
