# -*- coding: UTF-8 -*-
import os
from django.shortcuts import render
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter


from code_reading.models import PROJECTS_DIR, Project


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
    def get(self, request, project_directory):
        project, created = Project.objects.get_or_create(directory=project_directory)
        if created:
            project.name = project.directory
            project.save()
        if not project.analysed:
            project.analyse_project()
        pwd = request.GET.get('pwd', '')
        file = request.GET.get('file', '')
        formatted_content = ''
        template = 'code_reading/project_details.html'

        if not pwd:
            absolute_pwd = project.absolute_project_path
        else:
            absolute_pwd = os.path.join(project.absolute_project_path, pwd)
        
        if file:
            file_path = os.path.join(absolute_pwd, file)
            formatted_content = self.get_file_content(file_path)
            template = 'code_reading/file_details.html'
            
        files, directories = get_names(absolute_pwd)
        directories = [{'name': d, 'pwd': os.path.join(pwd, d)} for d in directories]
        context = {
            'title': project.name,
            'project': project,
            'pwd': pwd,
            'files': files,
            'file': file,
            'formatted_content': formatted_content,
            'directories': directories,
        }
        return render(request, template, context)
    
    
    def get_file_content(self, file_path):
        file_content = open(file_path).read()
        lexer = get_lexer_for_filename(file_path)
        return highlight(file_content, lexer, HtmlFormatter(linenos='table'))
