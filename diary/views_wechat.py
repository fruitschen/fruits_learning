# -*- coding: UTF-8 -*-
from diary.views import *
import json
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers

class WechatDiaryDetails(DiaryDetails):
    @method_decorator(staff_member_required)
    def get(self, request, diary_date):
        context = self.get_context(request, diary_date)
        serializer = EventSerializer(context['events'], many=True)
        events = JSONRenderer().render(serializer.data)
        diary = context['diary']
        contents = [content.as_dict for content in diary.contents.all()]
        response = json.dumps({
            'events': events,
            'contents': contents,
        })
        return HttpResponse(response)



class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    event = serializers.CharField()
    hidden = serializers.BooleanField()
    is_task = serializers.BooleanField()
    is_done = serializers.BooleanField()
    memo = serializers.CharField()
    event_type = serializers.CharField()


