# coding: utf-8
from django.shortcuts import render
from reads.models import Read


def read_list(request):
    reads_items = Read.objects.all().order_by('-id')
    context = {
        'reads_items': reads_items,
    }
    return render(request, 'reads/read_list.html', context)


def read_details(request, read_slug):
    read = Read.objects.get(slug=read_slug)
    context = {
        'read': read,
    }
    return render(request, 'reads/read_details.html', context)
