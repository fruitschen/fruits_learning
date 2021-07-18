# -*- coding: UTF-8 -*-

from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    reverse_order = models.BooleanField('是否倒序排列?', default=False)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full"),
        FieldPanel('reverse_order', classname="")
    ]

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)
        blogpages = self.get_children().live()
        if self.reverse_order:
            blogpages = blogpages.order_by('-first_published_at')
        else:
            blogpages = blogpages.order_by('first_published_at')
        context['blogpages'] = blogpages
        return context


class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
    ]
