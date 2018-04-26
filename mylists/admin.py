from django.contrib import admin

from mylists.models import *


class ListItemInline(admin.TabularInline):
    model = ListItem


class MyListAdmin(admin.ModelAdmin):
    model = MyList
    list_editable = ['order', ]
    list_display = ['name', 'order', ]
    inlines = [ListItemInline, ]


admin.site.register(MyList, MyListAdmin)
