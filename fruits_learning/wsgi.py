"""
WSGI config for fruits_learning project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

from __future__ import absolute_import, unicode_literals

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fruits_learning.settings.dev")

application = get_wsgi_application()
application = WhiteNoise(application, root='/home/fruitschen/srv/fruits_learning/static')
