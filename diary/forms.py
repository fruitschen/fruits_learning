# -*- coding: UTF-8 -*-
from django import forms

from diary.models import DiaryText, DiaryImage


class DiaryTextForm(forms.ModelForm):

    class Meta:
        model = DiaryText
        fields = ['text', 'title']
        widgets = {
            'text': forms.Textarea(attrs={
                'cols': 60, 'rows': 10,
                'style': 'max-width:100%;',
                'placeholder': u'早上干啥了？出门去哪里了？上课没，上课发生什么事了？玩什么玩具了吗？讲什么书了？'
            }),
        }

class DiaryImageForm(forms.ModelForm):

    class Meta:
        model = DiaryImage
        fields = ['image', 'title']


class EventsRangeForm(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)
