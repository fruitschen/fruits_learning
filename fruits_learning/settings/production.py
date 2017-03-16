from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False


WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-prod.json'),
    },
}

try:
    from .local import *
except ImportError:
    pass
