from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

CORS_ALLOW_ALL_ORIGINS = True


# ==========================
# DATABASE
# ==========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==========================
# MEDIA
# ==========================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'