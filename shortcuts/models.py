

from django.db import models


class Shortcut(models.Model):
    title = models.CharField(max_length=128)
    link = models.CharField(max_length=512)
    order = models.IntegerField(default=1)
    memo = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order']

