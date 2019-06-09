# -*- coding: UTF-8 -*-
import os
from django.shortcuts import render
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View



PROJECTS_DIR = os.path.join(settings.BASE_DIR, 'data', 'projects')


def get_names(directory):
    """Returns list of file names within directory"""
    contents = os.listdir(directory)
    files, directories = [], []
    for item in contents:
        candidate = os.path.join(directory, item)
        if os.path.isdir(candidate):
            directories.append(item)
        else:
            files.append(item)
    return files, directories


class ProjectsIndex(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        files, projects = get_names(PROJECTS_DIR)
        context = {
            'projects': projects,
        }
        return render(request, 'code_reading/projects.html', context)
