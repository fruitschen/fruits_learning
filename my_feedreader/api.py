from django.shortcuts import redirect
import django_filters
from rest_framework.decorators import action
from rest_framework import serializers, viewsets, renderers
from rest_framework.response import Response
from rest_framework.reverse import reverse

from feedreader.models import Feed, Entry


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='entry-detail', read_only=True)
    mark_as_read = serializers.HyperlinkedIdentityField(view_name='entry-mark-as-read', read_only=True)
    feed_title = serializers.EmailField(source='feed.title', read_only=True)

    class Meta:
        model = Entry
        fields = (
            'absolute_url', 'feed', 'id', 'link', 'title', 'published_time', 'read_flag',
            'mark_as_read', 'feed_title', 'description',
        )

class EntryFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Entry
        fields = {
            'read_flag': ['exact', ],
            'feed': ['exact', ],
        }


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    filter_class = EntryFilter

    @action(detail=True, renderer_classes=[renderers.BrowsableAPIRenderer, renderers.JSONRenderer], url_path='mark-as-read',
                  methods=['post'])
    def mark_as_read(self, request, *args, **kwargs):
        entry = self.get_object()
        if not entry.read_flag:
            entry.read_flag = True
            entry.save()

        detail_url = reverse('entry-detail', args=(), kwargs={'pk':entry.pk})
        return redirect(detail_url)
        return Response(EntrySerializer(entry, context={'request': request}).data)


class FeedSerializer(serializers.HyperlinkedModelSerializer):
    absolute_url = serializers.HyperlinkedIdentityField(view_name='feed-detail', read_only=True)

    class Meta:
        model = Feed
        fields = ('absolute_url', 'id','title', 'link', 'last_polled_time', )


class FeedViewSet(viewsets.ModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
