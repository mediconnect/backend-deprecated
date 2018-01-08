"""
Django settings for medi_connect_site project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=$npbw7-7ra9*j@0m4197_(-_s6p4re3&yjfx!c-74f@-2i(wm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'django-env.enc4mpznbt.us-west-2.elasticbeanstalk.com',
    'localhost',
    '127.0.0.1'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'customer',
    'translator',
    'supervisor',
    'placement',
    'info',
    'django_js_reverse',
    'db_manager',
    'dynamic_form',
    'helper',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'medi_connect_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'templates/',
            'core/templates/core',
            'customer/templates/customer',
            'translator/templates/translator',
            'placement/templates/placement',
            'info/templates/info',
            'core/templates/registration',
            'chisim',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'medi_connect_site.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

if 'RDS_HOSTNAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            # use mysql database
            'ENGINE': 'django.db.backends.mysql',
            # create database named mediconnect when test on local machine
            'NAME': 'mediconnect',
            # create user
            'USER': 'root',
            'PASSWORD': 'password',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'


USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static', ),
)

LOGIN_REDIRECT_URL = '/'
STATIC_ROOT = '/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
DEBUG_MEDIA_ROOT = 'C:\Users\gabri\Desktop\Project\website\medi_connect_site/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'abcdefgdontreplyme@outlook.com'
SERVER_EMAIL = 'abcdefgdontreplyme@outlook.com'
EMAIL_HOST = 'smtp.office365.com'
EMAIL_HOST_USER = 'abcdefgdontreplyme@outlook.com'
EMAIL_HOST_PASSWORD = 'passwordABC'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

AUTHENTICATION_BACKENDS = ['backend.email_login.EmailLoginBackend']


# SOCIAL_AUTH_PIPELINE = (
#     'social.pipeline.social_auth.social_details',
#     'social.pipeline.social_auth.social_uid',
#     'social.pipeline.social_auth.auth_allowed',
#     'social_auth.backends.pipeline.social.social_auth_user',
#     'social_auth.backends.pipeline.misc.save_status_to_session',
#     'social_auth.backends.pipeline.user.create_user',
#     'social_auth.backends.pipeline.social.associate_user',
#     'social_auth.backends.pipeline.social.load_extra_data',
#     'social_auth.backends.pipeline.user.update_user_details',
#     'social_auth.backends.pipeline.misc.save_status_to_session',
# )
#
# AUTHENTICATION_BACKENDS = (
#     'social.backends.weixin.WeixinOAuth2',
#     'django.contrib.auth.backends.ModelBackend',
# )
#
# SOCIAL_AUTH_WEIXIN_KEY = 'wxeb25ffbff85039ec'
# SOCIAL_AUTH_WEIXIN_SECRET = '4eb522c55dfb9a84cc4a702656a4036b'



#Logging Configuration:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'development_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'media/django_dev.log',
            'formatter': 'verbose'
        },
        'production_logfile': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'media/django_production.log',
            'maxBytes' : 1024*1024*100, # 100MB
            'backupCount' : 5,
            'formatter': 'simple'
        },
        'dba_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false','require_debug_true'],
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'media/django_dba.log',
            'formatter': 'simple'
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },
    'loggers': {
        'mediconnect': {
            'handlers': ['development_logfile','production_logfile'],
         },
        'dba': {
            'handlers': ['dba_logfile'],
        },
        'django': {
            'handlers': ['development_logfile','production_logfile'],
        },
        'py.warnings': {
            'handlers': ['development_logfile'],
        },
    }
}