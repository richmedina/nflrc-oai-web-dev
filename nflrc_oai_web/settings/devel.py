import os
from .base import *

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nflrc-oai-web-dev-db',
        'USER': os.environ['DJANGODBUSER'],
        'PASSWORD': os.environ['DJANGODBUSER_PASSWORD'],
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.environ['WHOOSH_PATH']
    },
}

STATICFILES_DIRS = [BASE_DIR / '..' / 'static',]