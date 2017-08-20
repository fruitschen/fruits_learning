from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string


class Diary(models.Model):
    date = models.DateField()

    @property
    def max_content_order(self):
        if not self.contents.exists():
            return 0
        else:
            return self.contents.order_by('-order')[0].order


class DiaryContent(models.Model):
    diary = models.ForeignKey('Diary', related_name='contents')
    order = models.IntegerField(null=True)
    title = models.CharField(blank=True, max_length=128)
    content_attr = models.CharField(max_length=20)

    def save(self, **kwargs):
        if not self.order:
            self.order = self.diary.max_content_order + 1
        super(DiaryContent, self).save(**kwargs)

    def render(self):
        content_obj = getattr(self, self.content_attr)
        return content_obj.render()

    class Meta:
        ordering = ['order']


class DiaryText(DiaryContent):
    text = models.TextField()

    def render(self):
        return render_to_string('diary/include/content_text.html', {'content': self, })


class DiaryImage(DiaryContent):
    image = models.ImageField(upload_to='diary')

    def render(self):
        return render_to_string('diary/include/content_image.html', {'content': self, 'MEDIA_URL': settings.MEDIA_URL })

