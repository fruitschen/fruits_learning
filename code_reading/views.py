# -*- coding: UTF-8 -*-
import os
from django.shortcuts import render
from django.conf import settings
from fruits_learning.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views import View

from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

from code_reading.models import PROJECTS_DIR, Project, ProjectFile


def get_names(directory):
    """Returns list of file names within directory"""
    contents = os.listdir(directory)
    files, directories = [], []
    for item in contents:
        if item in Project.SKIP_PATHS:
            continue
        ext = os.path.splitext(item)[-1].replace('.', '')
        if ext in Project.SKIP_EXTENSIONS:
            continue
        candidate = os.path.join(directory, item)
        if os.path.isdir(candidate):
            directories.append(item)
        else:
            files.append(item)
    files.sort()
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
        context = self.get_context(request, project_directory)
        return render(request, context['template'], context)
    
    def get_file_content(self, file_path):
        file_content = open(file_path).read()
        lexer = get_lexer_for_filename(file_path)
        return highlight(file_content, lexer, HtmlFormatter(linenos='table'))

    def get_context(self, request, project_directory):
        project, created = Project.objects.get_or_create(directory=project_directory)
        if created:
            project.name = project.directory
            project.save()
        if not project.analysed:
            project.analyse_project()
        if not project.updated_timestamp or project.updated_timestamp < timezone.now() - timezone.timedelta(minutes=10):
            project.update()
        pwd = request.GET.get('pwd', '')
        file = request.GET.get('file', '')
        file_obj = None
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
            rel_file_path = os.path.join(pwd, file)
            file_obj = project.files.get(filepath=rel_file_path)
            files = directories = files_objects = []
        else:
            files, directories = get_names(absolute_pwd)
            files_paths = ['{}/{}'.format(pwd, f) for f in files]
            files_objects = project.files.filter(filepath__in=files_paths).order_by('filename')
            directories = [{'name': d, 'pwd': os.path.join(pwd, d)} for d in directories]
        context = {
            'title': project.name,
            'project': project,
            'pwd': pwd,
            'files': files,
            'file': file,
            'file_obj': file_obj,
            'files_objects': files_objects,
            'formatted_content': formatted_content,
            'directories': directories,
            'template': template,
        }
        return context
        
    @method_decorator(staff_member_required)
    def post(self, request, project_directory):
        context = self.get_context(request, project_directory)
        if request.POST.get('action') == 'mark_as_read':
            context['file_obj'].mark_as_read()
            
        return render(request, context['template'], context)
