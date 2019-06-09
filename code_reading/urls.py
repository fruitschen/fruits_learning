from django.conf.urls import *

from code_reading.views import *

urlpatterns = [
    url(r'^$', ProjectsIndex.as_view(), name='code_reading_index'),
    url(r'^projects/(?P<project>\w+)/$', ProjectDetails.as_view(), name='code_reading_project'),
]
