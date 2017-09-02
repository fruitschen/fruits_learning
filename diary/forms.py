# -*- coding: UTF-8 -*-
from django import forms

from diary.models import DiaryText, DiaryImage


class DiaryTextForm(forms.ModelForm):

    class Meta:
        model = DiaryText
        fields = ['text', 'title']


class DiaryImageForm(forms.ModelForm):

    class Meta:
        model = DiaryImage
        fields = ['image', 'title']


class EventsRangeForm(forms.Form):
    start = forms.DateField(required=False)
    end = forms.DateField(required=False)
