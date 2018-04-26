from django.contrib import admin

from mylists.models import *


class ListItemInline(admin.TabularInline):
    model = ListItem


class MyListAdmin(admin.ModelAdmin):
    model = MyList
    list_editable = ['name', 'order', ]
    list_display = ['id', 'name', 'order', ]
    inlines = [ListItemInline, ]


admin.site.register(MyList, MyListAdmin)
