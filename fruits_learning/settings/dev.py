

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-ikv$&1cfu0x6!)bde4+j2y8bv(5hl#oo(dq^45*=b%#11n10i'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Add debug toolbar
INTERNAL_IPS = ['127.0.0.1', ]
# MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware',] + MIDDLEWARE
# INSTALLED_APPS = ['debug_toolbar'] + INSTALLED_APPS

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
