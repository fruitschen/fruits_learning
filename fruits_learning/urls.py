

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

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
router.register(r'info', InfoViewSet, base_name='info')
router.register(r'info-source', InfoSourceViewSet)
router.register(r'feed', FeedViewSet)
router.register(r'entry', EntryViewSet)


urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^search/$', search_views.search, name='search'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^info/', include('info_collector.urls')),
    url(r'^code_reading/', include('code_reading.urls')),
    url(r'^stocks/', include('stocks.urls')),
    url(r'^investing/', include('investing.urls')),
    url(r'^reads/', include('reads.urls')),
    url(r'^diary/', include('diary.urls')),
    url(r'^contacts/', include('contacts.urls')),
    url(r'^tweets/$', weibo_backup.views.tweets, name='tweets'),

    url(r'^my_feedreader/$', my_feedreader, name='my_feedreader'),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^markdownx/', include('markdownx.urls')),
    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
