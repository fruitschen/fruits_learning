from django.conf.urls import url, include
from django.utils import timezone
from django.shortcuts import redirect
import django_filters
from rest_framework.decorators import action
from rest_framework import serializers, viewsets, renderers
from rest_framework.response import Response
from rest_framework.reverse import reverse

from info_collector.models import Info, InfoSource
from info_collector.views import info_reader, info_reader_mobile, info_reader_read_items


class InfoSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='info-detail', read_only=True)
    mark_as_read = serializers.HyperlinkedIdentityField(view_name='info-mark-as-read', read_only=True)
    star_url = serializers.HyperlinkedIdentityField(view_name='info-star', read_only=True)
    unstar_url = serializers.HyperlinkedIdentityField(view_name='info-unstar', read_only=True)
    source_name = serializers.EmailField(source='info_source.name')
    source_id = serializers.EmailField(source='info_source.id')
    content = serializers.CharField(source='safe_content')
    author_id = serializers.CharField(source='author.id')
    author_name = serializers.CharField(source='author.name')
    author_avatar = serializers.CharField(source='author.avatar_url')

    class Meta:
        model = Info
        fields = (
            'absolute_url', 'info_source', 'id', 'url', 'title', 'timestamp', 'original_timestamp', 'read_at', 'tags',
            'mark_as_read', 'star_url', 'unstar_url', 'source_name', 'source_id', 'starred', 'is_read', 'content',
            'author_id', 'author_name', 'author_avatar', 'create_read_url', 'important', 'length',
        )


class InfoFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Info
        fields = {
            'title': ['contains', ],
            'tags': ['contains', ],
            'is_read': ['exact', ],
            'starred': ['exact', ],
            'important': ['exact', ],
            'info_source': ['exact', ],
            'author': ['exact', ],
        }


class InfoViewSet(viewsets.ModelViewSet):
    serializer_class = InfoSerializer
    # filter_fields = ('read_at', )
    filter_class = InfoFilter

    def get_queryset(self):
        ordering = self.request.GET.get('ordering', None)
        query = Info.objects.all().filter(is_deleted=False).select_related('author')
        if ordering:
            query = query.order_by(ordering)
        return query

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        info_items = Info.objects.filter(id__in=request.POST.getlist('ids[]', []))
        info_items.update(is_read=True, read_at=timezone.now())
        return Response({'status': 'OK'})

    @action(detail=True, renderer_classes=[renderers.BrowsableAPIRenderer, renderers.JSONRenderer], url_path='mark-as-read',
                  methods=['post'])
    def mark_as_read(self, request, *args, **kwargs):
        info = self.get_object()
        if not info.read_at or not info.is_read:
            info.read_at = timezone.now()
            info.is_read = True
            info.save()

        detail_url = reverse('info-detail', args=(), kwargs={'pk':info.pk})
        return redirect(detail_url)
        return Response(InfoSerializer(info, context={'request': request}).data)

    @action(detail=True, renderer_classes=[renderers.BrowsableAPIRenderer, renderers.JSONRenderer],
                  url_path='star',
                  methods=['post'])
    def star(self, request, *args, **kwargs):
        info = self.get_object()
        if not info.starred:
            info.starred_at = timezone.now()
            info.starred = True
            info.save()

        detail_url = reverse('info-detail', args=(), kwargs={'pk': info.pk})
        return redirect(detail_url)
        return Response(InfoSerializer(info, context={'request': request}).data)

    @action(detail=True, renderer_classes=[renderers.BrowsableAPIRenderer, renderers.JSONRenderer],
                  url_path='unstar',
                  methods=['post'])
    def unstar(self, request, *args, **kwargs):
        info = self.get_object()
        if info.starred:
            info.starred_at = None
            info.starred = False
            info.save()
        detail_url = reverse('info-detail', args=(), kwargs={'pk': info.pk})
        return redirect(detail_url)
        return Response(InfoSerializer(info, context={'request': request}).data)


class InfoSourceSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='infosource-detail', read_only=True)

    class Meta:
        model = InfoSource
        fields = ('absolute_url', 'id', 'name', 'status', 'url', )


class InfoSourceViewSet(viewsets.ModelViewSet):
    queryset = InfoSource.objects.all().exclude(silence=True)
    serializer_class = InfoSourceSerializer


urlpatterns = [
    url(r'^reader/$', info_reader, name='info_reader'),
    url(r'^reader/mobile/$', info_reader_mobile, name='info_reader_mobile'),
    url(r'^reader/recent_read_items/$', info_reader_read_items, name='info_reader_read_items'),
]
