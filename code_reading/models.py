from __future__ import unicode_literals
import os
from collections import defaultdict

from django.conf import settings
from django.db import models


PROJECTS_DIR = os.path.join(settings.BASE_DIR, 'data', 'projects')


class Project(models.Model):
    name = models.CharField(max_length=256)
    directory = models.CharField(max_length=256)
    analysed = models.BooleanField(default=False)
    files_count = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name
    
    @property
    def absolute_project_path(self):
        return os.path.join(PROJECTS_DIR, self.directory)

    def analyse_project(self):
        return
        

class ProjectFile(models.Model):
    project = models.ForeignKey('Project', related_name='files')
    filepath = models.CharField(max_length=256)
    filename = models.CharField(max_length=128)
    ext = models.CharField(max_length=5)
    size = models.IntegerField(null=True)
    read = models.IntegerField(default=0)
    ignored = models.BooleanField(default=False)
    lines_count = models.IntegerField(null=True)
    
    def __unicode__(self):
        return self.filename
