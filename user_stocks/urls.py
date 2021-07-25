from django.conf.urls import *

from user_stocks.views import *

urlpatterns = [
    url(r'^$', stocks, name='user_stocks'),
    url(r'^accounts/(?P<account_slug>\w+)/$', account_details, name='user_account_details'),
    url(r'^accounts/(?P<account_slug>\w+)/take_snapshot/$', take_snapshot, name='user_take_snapshot'),
    url(r'^accounts/(?P<account_slug>\w+)/(?P<snapshot_number>\d+)/$', account_snapshot, name='user_account_snapshot'),
]
