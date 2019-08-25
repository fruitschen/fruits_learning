from __future__ import unicode_literals
import os
from collections import defaultdict

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone


PROJECTS_DIR = os.path.join(settings.BASE_DIR, 'data', 'projects')


class Project(models.Model):
    name = models.CharField(max_length=256)
    directory = models.CharField(max_length=256)
    analysed = models.BooleanField(default=False)
    files_count = models.IntegerField(default=0)
    py_files_count = models.IntegerField(default=0)
    py_files_read_count = models.IntegerField(default=0)
    py_lines_count = models.IntegerField(default=0)
    py_lines_read_count = models.IntegerField(default=0)
    updated_timestamp = models.DateTimeField(null=True, default=None)
    
    SKIP_PATHS = ['.git', 'migrations']
    SKIP_EXTENSIONS = ['pyc', 'egg-info']
    
    def __unicode__(self):
        return self.name
    
    @property
    def absolute_project_path(self):
        return os.path.join(PROJECTS_DIR, self.directory)

    def analyse_project(self):
        def process_dir(data, dir, files):
            if file in Project.SKIP_PATHS:
                return
            for file in files:
                path = os.path.join(dir, file)
                if not os.path.isdir(path):
                    ext = os.path.splitext(path)[-1].replace('.', '')
                    if ext in self.SKIP_EXTENSIONS:
                        continue
                    relative_path = path.replace(self.absolute_project_path, '')
                    if relative_path.startswith('/'):
                        relative_path = relative_path[1:]
                    file_obj = ProjectFile.objects.filter(project=self, filepath=relative_path)
                    if not file_obj.exists():
                        file_obj = ProjectFile(
                            project=self,
                            filepath=relative_path,
                            filename=file,
                            ext=ext,
                        )
                        file_obj.analyse_file()

        os.path.walk(self.absolute_project_path, process_dir, None)
        self.files_count = self.files.count()
        self.analysed = True
        self.save()
        return
    
    def update(self):
        py_files = self.files.filter(ext='py')
        py_files_read = py_files.filter(read__gt=0)
        self.py_files_count = py_files.count()
        self.py_files_read_count = py_files_read.count()
        self.py_lines_count = py_files.aggregate(total_lines_count=Sum('lines_count'))['total_lines_count']
        self.py_lines_read_count = py_files_read.aggregate(total_lines_count=Sum('lines_count'))['total_lines_count']
        self.updated_timestamp = timezone.now()
        self.save()
        

class ProjectFile(models.Model):
    project = models.ForeignKey('Project', related_name='files')
    filepath = models.CharField(max_length=256)
    filename = models.CharField(max_length=128)
    ext = models.CharField(max_length=5)
    size = models.IntegerField(null=True)
    read = models.IntegerField(default=0)
    ignored = models.BooleanField(default=False)
    lines_count = models.IntegerField(null=True)

    VALID_TYPES = ['py', 'js', 'css', 'html', ]
    
    def __unicode__(self):
        return self.filename

    def analyse_file(self):
        path = os.path.join(self.project.absolute_project_path, self.filepath)
        if self.ext in ProjectFile.VALID_TYPES:
            self.lines_count = len(open(path, 'r').readlines())
        self.save()
    
    def mark_as_read(self):
        self.read += 1
        self.save()
        self.project.update()
