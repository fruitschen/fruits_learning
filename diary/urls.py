from django.conf.urls import *

from diary.views import *

urlpatterns = [
    url(r'^$', DiaryIndex.as_view(), name='diary_index'),
    url(r'^list/$', DiaryList.as_view(), name='diary_list'),
    url(r'^events/$', DiaryEvents.as_view(), name='diary_events'),
    url(r'^todo/$', DiaryTodo.as_view(), name='diary_todo'),
    url(r'^details/(?P<diary_date>\d{4}-\d{2}-\d{2})/$', diary_details, name='diary_details'),
    url(r'^details/(?P<diary_id>\d+)/add_text/$', DiaryAddText.as_view(), name='diary_add_text'),
    url(r'^details/(?P<diary_id>\d+)/add_image/$', DiaryAddImage.as_view(), name='diary_add_image'),
    url(r'^edit_text/(?P<content_id>\d+)/$', DiaryEditText.as_view(), name='diary_edit_text'),
    url(r'^update_task/$', UpdateTaskView.as_view(), name='update_task'),
]
