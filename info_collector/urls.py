from django.conf.urls import url, include
from info_collector.models import Info
from rest_framework import serializers, viewsets

# Serializers define the API representation.
class InfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Info
        fields = ('url', 'title', 'original_timestamp', )

# ViewSets define the view behavior.
class InfoViewSet(viewsets.ModelViewSet):
    queryset = Info.objects.all()
    serializer_class = InfoSerializer

