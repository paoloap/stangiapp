"""
Django settings for jwtauth project.

Generated by 'django-admin startproject' using Django 3.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from celery.schedules import crontab
import jwtauth.tasks


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# REFRESH_TOKEN_SECRET = SECRET_KEY
SECRET_KEY = os.environ.get("SECRET_KEY")
REFRESH_TOKEN_SECRET = SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = int(os.environ.get("DEBUG", default=0))

# For ssl
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(" ")

PROTECTED_URL = "/protected/"
PROTECTED_ROOT = BASE_DIR / "tunnel"
DOWNLOAD_PATH = PROTECTED_ROOT / "down"
UPLOAD_PATH = PROTECTED_ROOT / "up"
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'django_extensions',
    'crispy_forms',
    'api',
    'manager'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

#ALLOWED_HOSTS = ['*']
CORS_ALLOW_CREDENTIALS = True 
CORS_ORIGIN_ALLOW_ALL = True
#CORS_ORIGIN_WHITELIST = ['http://10.0.0.3:8081']
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
     'api.verify.JWTAuthentication',
    ),    
    'DEFAULT_PERMISSION_CLASSES': (
    'rest_framework.permissions.IsAuthenticated',
    )
}

ROOT_URLCONF = 'jwtauth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('templates')), str(BASE_DIR.joinpath('build'))],
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



WSGI_APPLICATION = 'jwtauth.wsgi.application'


# Database
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("SQL_DATABASE"),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST"),
        "PORT": os.environ.get("SQL_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIR = [
  # Tell Django where to look for React's static files (css, js)
  os.path.join(BASE_DIR, "build/static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Seafile
SF_API_URL = os.environ.get("SF_API_URL")
SF_API_ACC = {
    'username': os.environ.get("SF_API_USER"),
    'password': os.environ.get("SF_API_PWD")
}

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

CELERY_BEAT_SCHEDULE = {
    "send_email_notify": {
        "task": "jwtauth.tasks.send_email_notify",
        "schedule": crontab(hour="*/24"),
    },
}

EmailBackend = os.environ.get("EMAIL_BACKEND")
EMAIL_BACKEND = "django.core.mail.backends.{}.EmailBackend".format(EmailBackend)
if EmailBackend == "smtp":
    EMAIL_HOST = os.environ.get("SMTP_SERVER")
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.environ.get("SMTP_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("SMTP_PASSWORD")
elif EmailBackend == "filebased":
    EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))

DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_SENDER")
ADMINS = [("Admin", os.environ.get("ADMIN_EMAIL")), ]

FRONTEND_URL = os.environ.get("FRONTEND")
