from django.conf.urls import *

from diary.views import *

urlpatterns = [
    url(r'^$', DiaryIndex.as_view(), name='diary_index'),
    url(r'^list/$', DiaryList.as_view(), name='diary_list'),
    url(r'^events/$', DiaryEvents.as_view(), name='diary_events'),
    url(r'^events_table/$', DiaryEventsTable.as_view(), name='diary_events_table'),
    url(r'^add_event/$', AddEvent.as_view(), name='diary_add_event'),
    url(r'^todo/$', DiaryTodo.as_view(), name='diary_todo'),
    url(r'^details/(?P<diary_date>\d{4}-\d{2}-\d{2})/$', diary_details, name='diary_details'),
    url(r'^details/(?P<diary_id>\d+)/add_text/$', DiaryAddText.as_view(), name='diary_add_text'),
    url(r'^details/(?P<diary_id>\d+)/add_image/$', DiaryAddImage.as_view(), name='diary_add_image'),
    url(r'^details/(?P<diary_id>\d+)/add_audio/$', DiaryAddAudio.as_view(), name='diary_add_audio'),
    url(r'^edit_text/(?P<content_id>\d+)/$', DiaryEditText.as_view(), name='diary_edit_text'),
    url(r'^update_task/$', UpdateTaskView.as_view(), name='update_task'),
    url(r'^delete_task/$', DeleteTaskView.as_view(), name='delete_task'),
    url(r'^update_exercise_log/$', UpdateExerciseLogView.as_view(), name='update_exercise_log'),
    url(r'^wechat/', include('diary.urls_wechat')),
]

