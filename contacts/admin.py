from .models import Contact, Email
from django.contrib import admin


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', ]


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_at', 'is_mailed', 'mailed_at', ]
