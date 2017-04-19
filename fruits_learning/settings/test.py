from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = True

SECRET_KEY = 'testing.'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

INTERNAL_IPS = ['127.0.0.1', ]


