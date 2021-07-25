# -*- coding: UTF-8 -*-
from datetime import timedelta

from django.db.models import Sum
from django.shortcuts import render
from fruits_learning.decorators import staff_member_required
from django.utils import timezone
from django.http import HttpResponseForbidden

from weibo_backup.models import Tweet


@staff_member_required
def tweets(request):
    tweets = Tweet.objects.all()
    context = {
        'tweets': tweets,
    }
    return render(request, 'tweets.html', context)
