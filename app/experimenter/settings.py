"""
Django settings for experimenter.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from decouple import config
from urllib.parse import urljoin


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)

HOSTNAME = config("HOSTNAME")

ALLOWED_HOSTS = [HOSTNAME]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.forms",
    "corsheaders",
    "raven.contrib.django.raven_compat",
    "rest_framework",
    "djangoformsetjs",
    "jquery",
    "widget_tweaks",
    "experimenter.experiments",
    "experimenter.notifications",
    "experimenter.openidc",
    "experimenter.projects",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dockerflow.django.middleware.DockerflowMiddleware",
    "experimenter.openidc.middleware.OpenIDCAuthMiddleware",
]

ROOT_URLCONF = "experimenter.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

WSGI_APPLICATION = "experimenter.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASS"),
        "HOST": config("DB_HOST"),
        "PORT": "5432",
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]

OPENIDC_EMAIL_HEADER = config("OPENIDC_HEADER")
OPENIDC_AUTH_WHITELIST = ("experiments-api-list",)


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(os.path.join(BASE_DIR, "served"), "static")

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "mozlog": {
            "()": "dockerflow.logging.JsonLogFormatter",
            "logger_name": "experimenter",
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "mozlog",
        }
    },
    "loggers": {
        "django.db": {
            "handlers": ["console"] if DEBUG else [],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}


# Sentry configuration
RAVEN_CONFIG = {
    "dsn": config("SENTRY_DSN"),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    # 'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}


# Django Rest Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "experimenter.openidc.middleware.OpenIDCRestFrameworkAuthenticator",
    ),
}

# CORS Security Header Config
CORS_ORIGIN_ALLOW_ALL = True

# reDash Rate Limit
# Number of dashboards to deploy per hour
DASHBOARD_RATE_LIMIT = 2

# Automated email destinations

# SMTP configuration
EMAIL_SENDER = config("EMAIL_SENDER")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = not DEBUG
EMAIL_USE_SSL = False

# Email to send to when an experiment is ready for review
EMAIL_REVIEW = config("EMAIL_REVIEW")

# Email to send to when an experiment is ready to ship
EMAIL_SHIP = config("EMAIL_SHIP")

# Bugzilla API Integration
BUGZILLA_HOST = config("BUGZILLA_HOST")
BUGZILLA_API_KEY = config("BUGZILLA_API_KEY")
BUGZILLA_CC_LIST = config("BUGZILLA_CC_LIST")
BUGZILLA_CREATE_PATH = "/rest/bug"
BUGZILLA_CREATE_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, BUGZILLA_CREATE_PATH), api_key=BUGZILLA_API_KEY
)
BUGZILLA_DETAIL_URL = urljoin(BUGZILLA_HOST, "/show_bug.cgi?id={id}")
BUGZILLA_COMMENT_URL = "{path}?api_key={api_key}".format(
    path=urljoin(BUGZILLA_HOST, "/rest/bug/{id}/comment"),
    api_key=BUGZILLA_API_KEY,
)

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")
REDIS_DB = config("REDIS_DB")

# Celery
CELERY_BROKER_URL = "redis://{host}:{port}/{db}".format(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB
)
