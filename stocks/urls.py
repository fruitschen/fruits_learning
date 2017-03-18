from django.conf.urls import *

from stocks.views import *

urlpatterns = [
    url(r'^$', stocks, name='stocks'),
    url(r'^pair_details/(?P<pair_id>\d+)/$', pair_details, name='pair_details'),
    url(r'^pair_list/$', pair_list, name='pair_list'),
    url(r'^accounts/(?P<account_slug>\w+)/$', account_details, name='account_details'),
]


