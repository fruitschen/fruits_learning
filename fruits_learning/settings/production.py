

from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

try:
    from .local import *
except ImportError:
    pass

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json'),
    },
}
