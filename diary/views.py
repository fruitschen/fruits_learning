# -*- coding: UTF-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.reverse import reverse

from datetime import date, timedelta, datetime

from diary.models import (
    Diary, DiaryContent, DiaryText, WEEKDAY_DICT, Event, DATE_FORMAT, EVENT_TYPES, Exercise, ExerciseLog, EventGroup
)
from diary.forms import DiaryTextForm, DiaryImageForm, DiaryAudioForm, EventsRangeForm, EventForm
from diary.utils import get_events_by_date
from tips.models import get_random_tip
from info_collector.models import Info


def base_diary_context():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    return {
        'today': today.strftime(DATE_FORMAT),
        'yesterday': yesterday.strftime(DATE_FORMAT),
        'tomorrow': tomorrow.strftime(DATE_FORMAT),
    }


class DiaryIndex(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        today = date.today()
        return diary_details(request, today.strftime(DATE_FORMAT))


class DiaryList(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        diary_items = Diary.objects.all().order_by('-date')
        context = {
            'title': u'日记列表',
            'hide_header_footer': True,
            'diary_items': diary_items,
        }
        context.update(base_diary_context())
        return render(request, 'diary/diary_list.html', context)


class DiaryDetails(View):

    @method_decorator(staff_member_required)
    def get(self, request, diary_date):
        context = self.get_context(request, diary_date)
        return render(request, 'diary/diary_details.html', context)

    def get_context(self, request, diary_date):
        diary_date = datetime.strptime(diary_date, DATE_FORMAT).date()
        diary_query = Diary.objects.filter(date=diary_date)
        commit = True
        today = date.today()
        if diary_date == today:
            title = 'Diary, today'
        else:
            title = 'Diary, {}'.format(date.strftime(diary_date, '%Y-%m-%d'))
        diary = None
        if diary_query.exists():
            diary = diary_query[0]
        elif diary_date <= today:
            diary = Diary.objects.create(date=diary_date)
        elif diary_date > today:
            diary = Diary(date=diary_date)
            commit = False
        hidden_events_count = 0
        tag = request.GET.get('tag', '')
        events = get_events_by_date(diary.date, tag=tag, commit=commit)
        tasks = filter(lambda e: e.is_task, events)
        tasks_all_done = not filter(lambda task: not task.is_done, tasks)
        now = datetime.now()
        for event in events:
            event.hidden = False
            if tasks_all_done and getattr(event, 'is_done', False):
                event.hidden = True
            if today == diary_date and event.end_hour:
                if now > datetime(
                        now.year, now.month, now.day,
                        int(event.end_hour),
                        int(event.end_min or 0)
                ):
                    event.hidden = True
            if getattr(event, 'hidden', False):
                hidden_events_count += 1

        events_by_groups = []
        event_groups = EventGroup.objects.all()
        for group in list(event_groups) + [None]:
            group_events = filter(lambda e: e.group == group, events)
            if group_events:
                events_by_groups.append({
                    'group': group,
                    'events': group_events,
                })

        exercises_logs = ExerciseLog.objects.filter(date=diary_date)
        done_any_exercise = False
        if diary_date == today and not exercises_logs:
            exercises = Exercise.objects.all()
            for exercise in exercises:
                ex_log, created = ExerciseLog.objects.get_or_create(exercise=exercise, date=diary_date)
            exercises_logs = ExerciseLog.objects.filter(date=diary_date)
        done_any_exercise = exercises_logs.filter(times__gt=0).exists()

        editting = request.GET.get('editting', False)

        warnings = []

        yesterday = today - timedelta(days=1)
        if not DiaryContent.objects.filter(diary__date=yesterday).exists():
            warnings.append(u'昨天还没记日记!')
        if now.hour > 19 and diary_date == today and not diary.contents.all().exists():
            warnings.append(u'今天还没记日记!')

        tip = None
        if request.user.id == 1:
            tip = get_random_tip()

        unread_info_count = Info.objects.filter(is_read=False).count()
        event_form = EventForm(initial={'event_date': diary.date})

        context = {
            'title': title,
            'warnings': warnings,
            'tag': tag,
            'hide_header_footer': True,
            'hidden_events_count': hidden_events_count,
            'diary': diary,
            'weekday': WEEKDAY_DICT[str(diary.date.weekday())],
            'events': events,
            'events_by_groups': events_by_groups,
            'text_form': DiaryTextForm(),
            'image_form': DiaryImageForm(),
            'audio_form': DiaryAudioForm(),
            'event_form': event_form,
            'editting': editting,
            'tasks_all_done': tasks_all_done,
            'exercises_logs': exercises_logs,
            'done_any_exercise': done_any_exercise,
            'tip': tip,
            'unread_info_count': unread_info_count,
        }
        context.update(base_diary_context())
        return context


diary_details = DiaryDetails.as_view()


class DiaryAddText(View):
    @method_decorator(staff_member_required)
    def get(self, request, diary_id):
        diary = Diary.objects.get(id=diary_id)
        text_form = DiaryTextForm()
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'text_form': text_form,
        }
        return render(request, 'diary/include/diary_add_text.html', context)

    @method_decorator(staff_member_required)
    def post(self, request, diary_id):
        diary = Diary.objects.get(id=diary_id)
        text_form = DiaryTextForm(request.POST)
        if text_form.is_valid():
            diary_content = text_form.save(commit=False)
            diary_content.diary = diary
            diary_content.content_attr = 'diarytext'
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date,))
                return redirect(diary_details_url)
        else:
            context = {
                'hide_header_footer': True,
                'diary': diary,
                'text_form': text_form,
            }
            return render(request, 'diary/include/diary_add_text.html', context)


class DiaryAddImage(View):
    @method_decorator(staff_member_required)
    def get(self, request, diary_id):
        diary = Diary.objects.get(id=diary_id)
        image_form = DiaryImageForm()
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'image_form': image_form,
        }
        return render(request, 'diary/include/diary_add_image.html', context)

    @method_decorator(staff_member_required)
    def post(self, request, diary_id):
        diary = Diary.objects.get(id=diary_id)
        image_form = DiaryImageForm(request.POST, request.FILES)
        if image_form.is_valid():
            diary_content = image_form.save(commit=False)
            diary_content.diary = diary
            diary_content.content_attr = 'diaryimage'
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date,))
                return redirect(diary_details_url)
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'image_form': image_form,
        }
        return render(request, 'diary/include/diary_add_image.html', context)


class DiaryAddAudio(View):
    @method_decorator(staff_member_required)
    def get(self, request, diary_id):
        diary = Diary.objects.get(id=diary_id)
        audio_form = DiaryAudioForm()
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'audio_form': audio_form,
        }
        return render(request, 'diary/include/diary_add_audio.html', context)

    @method_decorator(staff_member_required)
    def post(self, request, diary_id):
        diary = Diary.objects.get(id=diary_id)
        audio_form = DiaryAudioForm(request.POST, request.FILES)
        if audio_form.is_valid():
            diary_content = audio_form.save(commit=False)
            diary_content.diary = diary
            diary_content.content_attr = 'diaryaudio'
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date,))
                return redirect(diary_details_url)
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'audio_form': audio_form,
        }
        return render(request, 'diary/include/diary_add_audio.html', context)


class DiaryEditText(View):
    @method_decorator(staff_member_required)
    def get(self, request, content_id):
        text_content = DiaryText.objects.get(id=content_id)
        diary = text_content.diary
        text_form = DiaryTextForm(instance=text_content)
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'text_content': text_content,
            'text_form': text_form,
        }
        return render(request, 'diary/include/diary_edit_text.html', context)

    @method_decorator(staff_member_required)
    def post(self, request, content_id):
        text_content = DiaryText.objects.get(id=content_id)
        diary = text_content.diary
        text_form = DiaryTextForm(request.POST, instance=text_content)
        if text_form.is_valid():
            diary_content = text_form.save(commit=False)
            diary_content.save()
            if request.is_ajax():
                return HttpResponse(diary_content.render())
            else:
                diary_details_url = reverse('diary_details', args=(diary.formatted_date,))
                return redirect(diary_details_url)
        context = {
            'hide_header_footer': True,
            'diary': diary,
            'text_content': text_content,
            'text_form': text_form,
        }
        return render(request, 'diary/include/diary_edit_text.html', context)


class DiaryEvents(View):
    @method_decorator(staff_member_required)
    def get(self, request):
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
            'title': u'日记 - 事件列表',
            'hide_header_footer': True,
            'days_and_events': days_and_events,
            'event_types': event_types,
            'selected_type': selected_type,
            'form': form,
            'shortcuts': shortcuts,
        }
        context.update(base_diary_context())
        return render(request, 'diary/events.html', context)


class UpdateTaskView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateTaskView, self).dispatch(request, *args, **kwargs)

    @method_decorator(staff_member_required)
    def post(self, request):
        task_id = request.POST.get('event_id', None)
        task = Event.objects.get(id=task_id)
        done = request.POST.get('checked', False)
        if done.lower() == 'true':
            task.is_done = True
        elif done.lower() == 'false':
            task.is_done = False
        task.save()
        return HttpResponse('Task Updated. ')


class DiaryTodo(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        todo_items = Event.objects.filter(event_date__isnull=True)
        todo_items = sorted(todo_items, key=lambda x:  x.priority)
        todo_items = sorted(todo_items, key=lambda x:  x.is_done)
        context = {
            'hide_header_footer': True,
            'title': 'TODO',
            'events': todo_items,
        }
        context.update(base_diary_context())
        return render(request, 'diary/todo.html', context)


class UpdateExerciseLogView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateExerciseLogView, self).dispatch(request, *args, **kwargs)

    @method_decorator(staff_member_required)
    def post(self, request):
        log_id = request.POST.get('log_id', None)
        ex_log = ExerciseLog.objects.get(id=log_id)
        ex_log.times += 1
        ex_log.save()
        return HttpResponse('Exercise Log Updated. ')


class AddEvent(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        initial = {
            'event_date': date.today(),
        }
        event_form = EventForm(initial=initial)
        context = {
            'hide_header_footer': True,
            'event_form': event_form,
        }
        return render(request, 'diary/include/add_event_form.html', context)

    @method_decorator(staff_member_required)
    def post(self, request):
        event_form = EventForm(request.POST)
        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.event_type = 'manual'
            event.save()
            diary_details_url = reverse('diary_details', args=(event.formatted_date,))
            return redirect(diary_details_url)
        else:
            context = {
                'hide_header_footer': True,
                'event_form': event_form,
            }
            return render(request, 'diary/include/add_event_form.html', context)
