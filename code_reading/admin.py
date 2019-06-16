from django.contrib import admin

from code_reading.models import Project, ProjectFile


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_filter = ['analysed']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['project', 'filepath', ]
    list_filter = ['project', 'ext', 'read']
