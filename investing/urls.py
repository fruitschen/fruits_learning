from django.conf.urls import *

from investing.views import *

urlpatterns = [
    url(r'^fund_value_estimation/$', fund_value_estimation, name='fund_value_estimation'),
    url(r'^fund_value_estimation/(?P<code>\d+)/$', fund_value_estimation, name='fund_value_estimation'),
    url(r'^compound_interest/$', compound_interest, name='compound_interest'),
]
