# -*- coding: UTF-8 -*-

import random

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = 'Categories'


class Source(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Tip(models.Model):
    content = models.CharField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.PROTECT)
    source = models.ForeignKey('Source', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.content


class LongTip(models.Model):
    tip = models.OneToOneField('Tip', related_name='long_tip', on_delete=models.CASCADE)
    text = models.TextField()


def get_random_tip():
    max_id = Tip.objects.aggregate(models.Max('id'))['id__max']
    random_id = random.randint(1, max_id)
    tip = Tip.objects.filter(id__lte=random_id).order_by('-id')[0]
    return tip
