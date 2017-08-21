from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from rest_framework.reverse import reverse

from datetime import date, timedelta

from diary.models import Diary, DiaryText, WEEKDAY_DICT, Event
from diary.forms import DiaryTextForm, DiaryImageForm
from diary.utils import get_events_by_date


@staff_member_required
def diary_index(request):
    today = date.today()
    today_diary, created = Diary.objects.all().get_or_create(date=today)
    events = get_events_by_date(today, commit=True)
    recent_diary_items = Diary.objects.all().order_by('-id')[:5]
    context = {
        'today_diary': today_diary,
        'weekday': WEEKDAY_DICT[str(today.weekday())],
        'events': events,
        'recent_diary_items': recent_diary_items,
    }
    return render(request, 'diary/diary_index.html', context)


@staff_member_required
def diary_list(request):
    diary_items = Diary.objects.all().order_by('-id')
    context = {
        'diary_items': diary_items,
    }
    return render(request, 'diary/diary_list.html', context)


@staff_member_required
def diary_details(request, diary_id):
    diary = Diary.objects.get(id=diary_id)
    events = get_events_by_date(diary.date, commit=True)
    editting = request.GET.get('editting', False)
    context = {
        'diary': diary,
        'weekday': WEEKDAY_DICT[str(diary.date.weekday())],
        'events': events,
        'text_form': DiaryTextForm(),
        'image_form': DiaryImageForm(),
        'editting': editting,
    }
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
                diary_details_url = reverse('diary_details', args=(diary_id, ))
                return redirect(diary_details_url)
    else:
        text_form = DiaryTextForm()
    context = {
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
                diary_details_url = reverse('diary_details', args=(diary_id, ))
                return redirect(diary_details_url)
    else:
        image_form = DiaryImageForm()
    context = {
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
                diary_details_url = reverse('diary_details', args=(diary.id, ))
                return redirect(diary_details_url)
    else:
        text_form = DiaryTextForm(instance=text_content)
    context = {
        'diary': diary,
        'text_content': text_content,
        'text_form': text_form,
    }
    return render(request, 'diary/include/diary_edit_text.html', context)


@staff_member_required
def diary_events(request):
    today = date.today()
    days = []
    days_and_events = []
    for i in range(32):
        days.append(today + timedelta(days=i))
    for day in days:
        events = get_events_by_date(day)
        days_and_events.append({
            'day': day,
            'weekday': WEEKDAY_DICT[str(day.weekday())],
            'events': events,
        })

    context = {
        'days_and_events': days_and_events,
    }
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
