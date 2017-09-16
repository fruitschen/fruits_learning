from django.contrib import admin

from tips.models import *


class LongTipInline(admin.TabularInline):
    model = LongTip


class TipAdmin(admin.ModelAdmin):
    model = Tip
    list_display_links = ['content']
    list_editable = ['source', 'category']
    list_display = ['source', 'category', 'content', ]
    list_filter = ['source', 'category']
    inlines = [LongTipInline, ]


class CategoryAdmin(admin.ModelAdmin):
    pass


class SourceAdmin(admin.ModelAdmin):
    pass


class LongTipAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tip, TipAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(LongTip, LongTipAdmin)
