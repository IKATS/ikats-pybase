"""
Copyright 2018-2019 CS Systèmes d'Information

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%^hzdv7krajw2no2jjwk=ek3jos@pra89e4+^yhev!+cxqt#f$'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.algo.catalogue',
    'apps.algo.custom',
    'apps.algo.execute',
]

# Application definition

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # disabled general protection: 'django.middleware.csrf.CsrfViewMiddleware',
    # see https://docs.djangoproject.com/fr/1.8/ref/csrf
    #     - see how to activate specifically CSRF protection: decorator @csrf_protect
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'ikats_processing.urls'
URL_PATH_IKATS_ALGO = "/ikats/algo"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
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

WSGI_APPLICATION = 'ikats_processing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ikats',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'ikats',
        'PASSWORD': 'ikats',
        'HOST': os.environ['POSTGRES_HOST'],
        'PORT': int(os.environ['POSTGRES_PORT']),
        'TEST': {
            'NAME':'ikats',
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Activate global static files: resources shared by several apps
#   Note: these folders are managed in conf !!!
#
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# STATIC_ROOT: will be used at deployment step: by command 'manage.py collectstatic'
#   This command gathers the different static folders
#   Note: folder STATIC_ROOT is not managed in conf !!!
#
STATIC_ROOT = os.path.join(BASE_DIR, "deploy", "static")


JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pylint',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Django is client of resource manager
IKATS_RESOURCE_SERVER = {
    'HOST': os.environ['TDM_HOST'],
    'PORT': int(os.environ['TDM_PORT'])
}

USE_X_FORWARDED_HOST = True

# -----------------------
# LOGGING initialization
# -----------------------
# INT environment
# -----------------------
# Beware : there are changes from Django 1.8 to 1.9
#
# See with Django 1.8: https://docs.djangoproject.com/fr/1.8/topics/logging
#
# -----------------------
# Note1: verboselight formatter has no information about pid and thread id,
#        contrary to verbose formatter
#
# Note2: to follow SQL requests handled by django: switch level to 'DEBUG' on 'django' logger
#
REP_LOGS = "/logs"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'verboselight': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'ikats-processing-file': {
            'class': 'logging.FileHandler',
            'filename': REP_LOGS + '/ikats_processing.log',
            'formatter': 'verbose'
        },
        'django-file': {
            'class': 'logging.FileHandler',
            'filename': REP_LOGS + '/ikats_django.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'ikats_processing': {
            'handlers': ['ikats-processing-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'apps': {
            'handlers': ['ikats-processing-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'ikats': {
            'handlers': ['ikats-processing-file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'ikats_pre': {
            'handlers': ['ikats-processing-file'],
            'level': 'DEBUG',
            'propagate': True,
        },

    },
}
