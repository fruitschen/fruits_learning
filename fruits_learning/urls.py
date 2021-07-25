from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path


import info_collector
import rest_framework
import investing
import reads
import diary
import contacts
import django_rq
import markdownx
import stocks
import weibo_backup.views

import rest_framework
import weibo_backup.views
from search import views as search_views
from investing import views as investing_views
from my_feedreader.views import my_feedreader
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from rest_framework import routers
from info_collector.urls import InfoViewSet, InfoSourceViewSet
from my_feedreader.api import FeedViewSet, EntryViewSet
router = routers.DefaultRouter()
router.register(r'info', InfoViewSet, basename='info')
router.register(r'info-source', InfoSourceViewSet)
router.register(r'feed', FeedViewSet)
router.register(r'entry', EntryViewSet)


urlpatterns = [
    path(r'django-admin/', admin.site.urls),
    path(r'admin/', include(wagtailadmin_urls)),
    path(r'documents/', include(wagtaildocs_urls)),
    url(r'^search/$', search_views.search, name='search'),
    path(r'api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(r'info/', include(info_collector.urls)),
    path(r'stocks/', include('stocks.urls')),
    path(r'user_stocks/', include('user_stocks.urls')),
    path(r'investing/', include('investing.urls')),
    path(r'reads/', include('reads.urls')),
    path(r'diary/', include('diary.urls')),
    path(r'contacts/', include('contacts.urls')),
    url(r'^tweets/$', weibo_backup.views.tweets, name='tweets'),

    url(r'^my_feedreader/$', my_feedreader, name='my_feedreader'),
    path(r'django-rq/', include('django_rq.urls')),
    path(r'markdownx/', include('markdownx.urls')),
    path(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
