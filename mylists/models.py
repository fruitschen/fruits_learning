from __future__ import unicode_literals

from django.db import models


class MyList(models.Model):
    name = models.CharField(max_length=64)
    order = models.IntegerField(default=10)

    class Meta:
        ordering = ['order', ]


class ListItem(models.Model):
    my_list = models.ForeignKey(MyList)
    content = models.CharField(max_length=256)
    order = models.IntegerField(default=10)


    def __unicode__(self):
        return ''.format(self.my_list.name, self.content)

    class Meta:
        ordering = ['order', ]
