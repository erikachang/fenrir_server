"""
Django settings for volky_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ADMINS = (('Support', 'team@miceware.co'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['localhost',
                 '127.0.0.1']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'volky_server',
    'vauth',
    'users',
    'volky',
    'reserved_names',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
)

AUTHENTICATION_BACKENDS = (
    'vauth.backends.ApiTokenAuthentication',
    'vauth.backends.BasicAuthentication',
    'vauth.backends.FacebookAuthentication',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

ROOT_URLCONF = 'volky_server.urls'

WSGI_APPLICATION = 'volky_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fenrirdb',
        'USER': 'wolf_alpha',
        'PASSWORD': os.environ['PSQL_PWD'],
        'HOST': 'fenrirdb',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# E-mail config
MAILGUN_DOMAIN = 'volky.me'
MAILGUN_ENDPOINT = 'https://api.mailgun.net/v2/%s/messages' % MAILGUN_DOMAIN
MAILGUN_APITOKEN = os.environ['MAILGUN_APITOKEN']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MEDIA_ROOT = '/media/volky/user_photos/'
MEDIA_URL = '/user_photos/'

APNS = {
    'CERTIFICATE': '/opt/volky/apns.pem',
    'ENVIRONMENT': 'production',
    'FEEDBACK': ('feedback.push.apple.com', 2196),
    'GATEWAY': ('gateway.push.apple.com', 2195)
}

APNS_MAX_WORKERS = 2
