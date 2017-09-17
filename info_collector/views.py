import json
from datetime import datetime
from datetime import timedelta
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from info_collector.models import Info
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from diary.models import DATE_FORMAT


def info_reader(request):
    context = {

    }
    return render(request, 'info_collector/info_reader.html', context)


def info_reader_read_items(request):
    a_week_ago = timezone.now() - timedelta(days=7)
    start = a_week_ago
    if request.GET.get('start_date', False):
        start_date = request.GET.get('start_date')
        start_date = datetime.strptime(start_date, DATE_FORMAT).date()
        start = start_date
    recent_read_items = Info.objects.filter(read_at__gte=start, is_read=True)
    serializer = ReadInfoSerializer(recent_read_items, many=True)
    return HttpResponse(JSONRenderer().render(serializer.data))


class ReadInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    read_at = serializers.DateTimeField()
