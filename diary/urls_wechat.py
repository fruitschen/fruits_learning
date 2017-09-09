from django.conf.urls import *

from diary.views_wechat import *

urlpatterns = [
    url(r'^details/(?P<diary_date>\d{4}-\d{2}-\d{2})/$', WechatDiaryDetails.as_view(), name='diary_details_wechat'),
]

