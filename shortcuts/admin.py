from django.contrib import admin
from .models import Shortcut


class ShortcutAdmin(admin.ModelAdmin):
    model = Shortcut
    list_display = ['title', 'link', 'order']
    list_editable = ['order']

admin.site.register(Shortcut, ShortcutAdmin)
