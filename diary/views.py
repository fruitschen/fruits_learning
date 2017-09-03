# -*- coding: UTF-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.reverse import reverse

from datetime import date, timedelta, datetime

from diary.models import Diary, DiaryText, WEEKDAY_DICT, Event, DATE_FORMAT, EVENT_TYPES
from diary.forms import DiaryTextForm, DiaryImageForm, EventsRangeForm
from diary.utils import get_events_by_date


def base_diary_context():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    return {
        'today': today.strftime(DATE_FORMAT),
        'yesterday': yesterday.strftime(DATE_FORMAT),
        'tomorrow': tomorrow.strftime(DATE_FORMAT),
    }

@staff_member_required
def diary_index(request):
    today = date.today()
    return diary_details(request, today.strftime(DATE_FORMAT))


@staff_member_required
def diary_list(request):
    diary_items = Diary.objects.all().order_by('-date')
    context = {
        'hide_header_footer': True,
        'diary_items': diary_items,
    }
    context.update(base_diary_context())
    return render(request, 'diary/diary_list.html', context)


@staff_member_required
def diary_details(request, diary_date):
    diary_date = datetime.strptime(diary_date, DATE_FORMAT).date()
    diary_query = Diary.objects.filter(date=diary_date)
    commit = True
    today = date.today()
    if diary_query.exists():
        diary = diary_query[0]
    elif diary_date <= today:
        diary = Diary.objects.create(date=diary_date)
    elif diary_date > today:
        diary = Diary(date=diary_date)
        commit = False
    events = get_events_by_date(diary.date, commit=commit)
    tasks = filter(lambda event: event.is_task, events)
    tasks_all_done = not filter(lambda task: not task.is_done,tasks)
    editting = request.GET.get('editting', False)
    context = {
        'hide_header_footer': True,
        'diary': diary,
        'weekday': WEEKDAY_DICT[str(diary.date.weekday())],
        'events': events,
        'text_form': DiaryTextForm(),
        'image_form': DiaryImageForm(),
        'editting': editting,
        'tasks_all_done': tasks_all_done,
    }
    context.update(base_diary_context())
    return render(request, 'diary/diary_details.html', context)


@staff_member_required
def diary_add_text(request, diary_id):
    diary = Diary.objects.get(id=diary_id)
    if request.method == "POST":
        text_form = DiaryTextForm(request.POST)
        if text_form.is_valid():
            diary_content = text_form.save(commit=False)
            diary_content.diary = diary
            diary_content.content_attr = 'diarytext'
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date, ))
                return redirect(diary_details_url)
    else:
        text_form = DiaryTextForm()
    context = {
        'hide_header_footer': True,
        'diary': diary,
        'text_form': text_form,
    }
    return render(request, 'diary/include/diary_add_text.html', context)


@staff_member_required
def diary_add_image(request, diary_id):
    diary = Diary.objects.get(id=diary_id)
    if request.method == "POST":
        image_form = DiaryImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            diary_content = image_form.save(commit=False)
            diary_content.diary = diary
            diary_content.content_attr = 'diaryimage'
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date, ))
                return redirect(diary_details_url)
    else:
        image_form = DiaryImageForm()
    context = {
        'hide_header_footer': True,
        'diary': diary,
        'image_form': image_form,
    }
    return render(request, 'diary/include/diary_add_image.html', context)


@staff_member_required
def diary_edit_text(request, content_id):
    text_content = DiaryText.objects.get(id=content_id)
    diary = text_content.diary
    if request.method == "POST":
        text_form = DiaryTextForm(request.POST, instance=text_content)
        if text_form.is_valid():
            diary_content = text_form.save(commit=False)
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date, ))
                return redirect(diary_details_url)
    else:
        text_form = DiaryTextForm(instance=text_content)
    context = {
        'hide_header_footer': True,
        'diary': diary,
        'text_content': text_content,
        'text_form': text_form,
    }
    return render(request, 'diary/include/diary_edit_text.html', context)


@staff_member_required
def diary_events(request):
    event_types = EVENT_TYPES
    selected_type = request.GET.get('event_type', None)

    today = date.today()
    default_start = today
    default_end = default_start + timedelta(days=42)
    form = EventsRangeForm(initial={'start': default_start, 'end': default_end})
    if request.GET:
        form = EventsRangeForm(request.GET)
        form.is_valid()
        start = form.cleaned_data.get('start', None) or default_start
        default_end = start + timedelta(days=42)
        end = form.cleaned_data.get('end', None) or default_end
    else:
        start = default_start
        end = default_end

    shortcuts = [
        [u'一周以前', today - timedelta(days=7),],
        [u'一月以前', today - timedelta(days=30),],
    ]

    current_day = start
    days = []
    days_and_events = []
    while current_day < end:
        days.append(current_day)
        current_day += timedelta(days=1)
    for day in days:
        events = get_events_by_date(day)
        if selected_type:
            events = filter(lambda event:event.event_type==selected_type, events)
        if events:
            days_and_events.append({
                'day': day,
                'weekday': WEEKDAY_DICT[str(day.weekday())],
                'events': events,
            })

    context = {
        'hide_header_footer': True,
        'days_and_events': days_and_events,
        'event_types': event_types,
        'selected_type': selected_type,
        'form': form,
        'shortcuts': shortcuts,
    }
    context.update(base_diary_context())
    return render(request, 'diary/events.html', context)


@staff_member_required
@csrf_exempt
def update_task(request):
    task_id = request.POST.get('event_id', None)
    task = Event.objects.get(id=task_id)
    done = request.POST.get('checked', False)
    if done.lower() == 'true':
        task.is_done = True
    elif done.lower() == 'false':
        task.is_done = False
    task.save()
    return HttpResponse('Task Updated. ')


@staff_member_required
def diary_todo(request):
    todo_items = Event.objects.filter(event_date__isnull=True)
    context = {
        'hide_header_footer': True,
        'events': todo_items,
    }
    context.update(base_diary_context())
    return render(request, 'diary/todo.html', context)
