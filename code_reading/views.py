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


class ProjectDetails(View):

    @method_decorator(staff_member_required)
    def get(self, request, project):
        absolute_project_path = os.path.join(PROJECTS_DIR, project)
        pwd = request.GET.get('pwd', '')
        if not pwd:
            absolute_pwd = absolute_project_path
        else:
            absolute_pwd = os.path.join(absolute_project_path, pwd)
        files, directories = get_names(absolute_pwd)
        directories = [{'name': d, 'pwd': os.path.join(pwd, d)} for d in directories]
        context = {
            'title': project,
            'project': project,
            'pwd': pwd,
            'files': files,
            'directories': directories,
        }
        return render(request, 'code_reading/project_details.html', context)
