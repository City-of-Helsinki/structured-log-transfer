"""
Django settings for structuredlogtransfer project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from enum import Enum

import environ

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class AuditLoggerType(str, Enum):
    SINGLE_COLUMN_JSON = "SINGLE_COLUMN_JSON"
    DJANGO_AUDITLOG = "DJANGO_AUDITLOG"


env = environ.Env(
    ALLOWED_HOSTS=(list, []),
    AUDIT_LOG_ENVIRONMENT=(str, ""),
    AUDIT_LOG_ORIGIN=(str, ""),
    AUDIT_LOGGER_TYPE=(AuditLoggerType, AuditLoggerType.SINGLE_COLUMN_JSON),
    AUDIT_TABLE_NAME=(str, "audit_logs"),
    CLEAR_AUDIT_LOG_ENTRIES=(bool, True),
    DATABASE_PASSWORD=(str, ""),
    DATABASE_URL=(str, ""),
    DATE_TIME_FIELD=(str, "date_time"),
    DATE_TIME_PARENT_FIELD=(str, "audit_event"),
    DB_USE_SSL=(bool, False),
    DEBUG=(bool, False),
    ELASTICSEARCH_APP_AUDIT_LOG_INDEX=(str, "app_audit_log"),
    ELASTICSEARCH_HOST=(str, ""),
    ELASTICSEARCH_PASSWORD=(str, ""),
    ELASTICSEARCH_PORT=(int, 0),
    ELASTICSEARCH_SCHEME=(str, "https"),
    ELASTICSEARCH_USERNAME=(str, ""),
    ENABLE_SEND_AUDIT_LOG=(bool, True),
    NEXT_PUBLIC_BACKEND_URL=(str, "https://localhost:8000"),
    SSL_CA=(str, ""),
    SSL_CERT=(str, ""),
    SSL_CIPHER=(str, ""),
    SSL_KEY=(str, ""),
    USE_X_FORWARDED_HOST=(bool, False),
    USER_TABLE_NAME=(str, "auth_user"),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4(e0ry+n%rad8^!i-+d1($9u_=wbvcz*iv5n)hc&omki(dne%h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Set user model (for django_auditlog)
AUTH_USER_MODEL = "log_transfer.User"
USER_TABLE_NAME = env("USER_TABLE_NAME")

# Audit logging
AUDIT_LOG_ORIGIN = env("AUDIT_LOG_ORIGIN")
AUDIT_LOG_ENVIRONMENT = env("AUDIT_LOG_ENVIRONMENT")
CLEAR_AUDIT_LOG_ENTRIES = env("CLEAR_AUDIT_LOG_ENTRIES")
ELASTICSEARCH_APP_AUDIT_LOG_INDEX = env("ELASTICSEARCH_APP_AUDIT_LOG_INDEX")
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST")
ELASTICSEARCH_PORT = 0

if env("ELASTICSEARCH_PORT"):
    ELASTICSEARCH_PORT = env("ELASTICSEARCH_PORT")
else:
    if ELASTICSEARCH_HOST.count(":") > 0:
        hostAndPort = ELASTICSEARCH_HOST.split(":", 1)
        ELASTICSEARCH_HOST = hostAndPort[0]
        ELASTICSEARCH_PORT = int(hostAndPort[1])

ELASTICSEARCH_USERNAME = env("ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = env("ELASTICSEARCH_PASSWORD")
ENABLE_SEND_AUDIT_LOG = env("ENABLE_SEND_AUDIT_LOG")
AUDIT_TABLE_NAME = env("AUDIT_TABLE_NAME")

# Field names for fetching the elastic timestamp from json data
DATE_TIME_PARENT_FIELD = env("DATE_TIME_PARENT_FIELD")
DATE_TIME_FIELD = env("DATE_TIME_FIELD")

# Scheme for connecting to elastic, for example: "http", or: "https"
ELASTICSEARCH_SCHEME = env("ELASTICSEARCH_SCHEME")

# What kind of audit logger type to use, defined in AuditLoggerType
AUDIT_LOGGER_TYPE = env("AUDIT_LOGGER_TYPE")

# Application definition

_first_party_apps = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

_third_party_apps = [
    "django_extensions",
]

if AUDIT_LOGGER_TYPE == AuditLoggerType.DJANGO_AUDITLOG:
    _third_party_apps.append("auditlog")

_project_apps = [
    "log_transfer",
]

INSTALLED_APPS = _first_party_apps + _third_party_apps + _project_apps

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'structuredlogtransfer.urls'

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

WSGI_APPLICATION = 'structuredlogtransfer.wsgi.application'




# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

dbenv=env.db()

if (env("DB_USE_SSL")):
  ssl_subpart = {}
  if (env("SSL_CA")):
    ssl_subpart['ssl-ca'] = env("SSL_CA")
  if (env("SSL_KEY")):
    ssl_subpart['key'] = env("SSL_KEY")
  if (env("SSL_CERT")):
    ssl_subpart['cert'] = env("SSL_CERT")
  if (env("SSL_CIPHER")):
    ssl_subpart['cipher'] = env("SSL_CIPHER")

  SSL_OPTS= {
     'OPTIONS': {
            'ssl': ssl_subpart
        }
  }
  DATABASES = {
    'default': {**dbenv,  **SSL_OPTS}
  }
else:
  DATABASES = {
    'default': dbenv
  }

if "PASSWORD" in DATABASES["default"] and DATABASES["default"]["PASSWORD"]:
  print("DB Password is set from db url")
else:
  print("DB Password is not set from db url")

forLog = DATABASES["default"].copy()
forLog["PASSWORD"]=""
print("Database config:", forLog)

if env("DATABASE_PASSWORD"):
  DATABASES["default"]["PASSWORD"]=env("DATABASE_PASSWORD")
  print("Set password from DATABASE_PASSWORD env")
else:
  print("Password not set from DATABASE_PASSWORD env")

# Replace the gis versions of db engines with regular ones, not used when reading logs even if the project otherwise uses these.
if "ENGINE" in DATABASES["default"]:
  if DATABASES["default"]["ENGINE"] == "django.contrib.gis.db.backends.postgis":
    DATABASES["default"]["ENGINE"]="django.db.backends.postgresql"

  if DATABASES["default"]["ENGINE"] == "django.contrib.gis.db.backends.mysql":
    DATABASES["default"]["ENGINE"]="django.db.backends.mysql"


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/srv/static'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
