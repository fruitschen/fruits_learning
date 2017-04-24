from django.conf.urls import *

from reads.views import *

urlpatterns = [
    url(r'^$', read_list, name='read_list'),
    url(r'^details/(?P<read_slug>.+)/$', read_details, name='read_details'),
]
