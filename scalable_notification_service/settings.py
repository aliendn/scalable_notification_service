import os
from pathlib import Path

import environ

######################
# Django config region
######################
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
# env configuration
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_URL = env('SERVER_ADDRESS')
ROOT_URLCONF = 'scalable_notification_service.urls'

DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

APPEND_SLASH = True

#############
# Apps region
#############
DJANGO_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

OTHER_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'silk',
]

PROJECT_APPS = [
    'apps.users',
    'apps.notification_service'
]

INSTALLED_APPS = DJANGO_APPS + OTHER_APPS + PROJECT_APPS

###################
# Middleware region
###################
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'silk.middleware.SilkyMiddleware',
]

##################
# Templates region
##################
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

####################
# WSGI and ASGI config region
####################
# WSGI_APPLICATION = 'scalable_notification_service.wsgi.application'
ASGI_APPLICATION = "scalable_notification_service.asgi.application"

#################
# DataBase region
#################
DATABASES = {'default': env.db()}

######################
# Auth password region
######################
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

##################
# PASSWORD_SERVICE
##################
GENERATED_PASSWORD_LENGTH = int(
    os.getenv("GENERATED_PASSWORD_LENGTH", 12)
)
VALID_PASSWORD_CHARACTERS = os.getenv(
    "VALID_PASSWORD_CHARACTERS",
    "abcdefghijklmnopqrstuvwxyz0123456789@&_"
)

#############################
# Internationalization region
#############################
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

###############
# Static region
###############
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

##############
# Media region
##############
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

##############
# Redis region
##############
REDIS_ADDRESS = env('REDIS_ADDRESS')

##############
# Email region
##############
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

##################
# MEMORY MANAGEMENTS
##################
DATA_UPLOAD_MAX_MEMORY_SIZE = 3000 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 3000 * 1024 * 1024
MAX_UPLOAD_SIZE = 3000 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1_000_000

##################
# Admin information's
##################
ADMIN_HEADER = env("ADMIN_HEADER", default='ADMIN PAGE HEADER')
ADMIN_INDEX_TITLE = env("ADMIN_INDEX_TITLE", default='ADMIN PAGE TITLE')

##################
# API Versions
##################
API_V1_PREFIX = 'api/v1/'

############
# DRF region
############
REST_FRAMEWORK = {
    'TIME_ZONE': 'UTC',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'MY project',
    'DESCRIPTION': 'MY project description',
    'VERSION': '0.0.1',
    'SERVE_INCLUDE_SCHEMA': False,
}
