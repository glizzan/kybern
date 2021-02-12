"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


ALLOWED_HOSTS = ['127.0.0.1', 'kybern.herokuapp.com', 'www.kybern.org', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # concord apps
    'concord',
    'concord.actions',
    'concord.communities',
    'concord.resources',
    'concord.permission_resources',
    'concord.conditionals',
    # kybern apps
    'accounts',
    'groups',
    # third party apps
    'django_registration',
    # django contrib stuff needs to be here so accounts can override default logout page
    'django.contrib.auth',
    'django.contrib.admin',
    'webpack_loader'
]

# CONCORD_APPS and KYBERN_APPS are used in logging
CONCORD_APPS = [
    'concord',
    'concord.actions',
    'concord.communities',
    'concord.resources',
    'concord.permission_resources',
    'concord.conditionals',
]
KYBERN_APPS = [
    'accounts',
    'groups',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'


# Custom configurations

LOGIN_REDIRECT_URL = "/profile/"
LOGIN_URL = '/login/'

ACCOUNT_ACTIVATION_DAYS = 14

TEMPLATE_LIBARIES = ['groups']  # template libraries must be stored as a template_library.py file in the top level of an app

DEFAULT_COMMUNITY_MODEL = "group"  # the main community/group model used


### Logging
import logging

# set default log level
DEFAULT_LOG_LEVEL_FOR_TESTS = "WARN"
DEFAULT_LOG_LEVEL = "WARN"
import sys
TESTING = sys.argv[1:2] == ['test']
LOG_LEVEL = DEFAULT_LOG_LEVEL_FOR_TESTS if TESTING else DEFAULT_LOG_LEVEL

# Generate loggers
loggers = {}
for app in CONCORD_APPS + KYBERN_APPS:
    loggers.update({app: {'handlers': ['console', 'file'], 'level': LOG_LEVEL}})
loggers[''] = {'handlers': ['console', 'file'], 'level': LOG_LEVEL}

# Override for specific apps using format loggers['concord.actions'] = {'handlers': ['console', 'file'], 'level': "DEBUG"}
# loggers['concord.actions'] = {'handlers': ['console', 'file'], 'level': "DEBUG"}
# loggers['concord.actions.utils'] = {'handlers': ['console', 'file'], 'level': "WARN"}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': '/tmp/debug.log'
        }
    },
    'loggers': loggers
}


# Check to see if we're in local development or production, and load appropriate settings

if os.environ.get("KYBERN_ENVIRONMENT") and os.environ.get("KYBERN_ENVIRONMENT") == "PRODUCTION":
    from .production_settings import *  # noqa: F403, F401
else:
    from .local_settings import *  # noqa: F403, F401


# Webpack stuffs

VUE_FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'vue/',  # must end with slash
        'STATS_FILE': os.path.join(VUE_FRONTEND_DIR, 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    }
}


RUN_HEADLESS = False
RUN_HEADLESS = True