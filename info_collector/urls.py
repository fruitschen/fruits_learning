from django.conf.urls import url, include
from django.utils import timezone
from django.shortcuts import redirect
import django_filters
from rest_framework.decorators import detail_route
from rest_framework import serializers, viewsets, renderers
from rest_framework.response import Response
from rest_framework.reverse import reverse

from info_collector.models import Info, InfoSource


class InfoSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='info-detail', read_only=True)
    mark_as_read = serializers.HyperlinkedIdentityField(view_name='info-mark-as-read', read_only=True)

    class Meta:
        model = Info
        fields = (
            'absolute_url', 'info_source', 'id', 'url', 'title', 'timestamp', 'original_timestamp', 'read_at',
            'mark_as_read',
        )


class InfoFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Info
        fields = {
            'is_read': ['exact', ],
            'info_source': ['exact', ],
        }


class InfoViewSet(viewsets.ModelViewSet):
    queryset = Info.objects.all()
    serializer_class = InfoSerializer
    # filter_fields = ('read_at', )
    filter_class = InfoFilter

    @detail_route(renderer_classes=[renderers.BrowsableAPIRenderer, renderers.JSONRenderer], url_path='mark-as-read')
    def mark_as_read(self, request, *args, **kwargs):
        info = self.get_object()
        if not info.read_at:
            info.read_at = timezone.now()
            info.is_read = True
            info.save()

        detail_url = reverse('info-detail', args=(), kwargs={'pk':info.pk})
        return redirect(detail_url)
        return Response(InfoSerializer(info, context={'request': request}).data)


class InfoSourceSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='infosource-detail', read_only=True)

    class Meta:
        model = InfoSource
        fields = ('absolute_url', 'name', 'status', 'url', )


class InfoSourceViewSet(viewsets.ModelViewSet):
    queryset = InfoSource.objects.all()
    serializer_class = InfoSourceSerializer

