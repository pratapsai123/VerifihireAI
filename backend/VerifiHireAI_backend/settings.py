"""
Django settings for VerifiHireAI_backend project.
"""

import os
from pathlib import Path


def _env_list(key: str, default: list[str]) -> list[str]:
    """Return a list from a comma-separated environment variable, falling back to default."""
    value = os.environ.get(key)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-this-in-production-12345")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["*"]

FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")


# Application definition

INSTALLED_APPS = [
#    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'api',
    'ai_assessments',
    'ai_candidates',
    'rest_framework_simplejwt',
]

# Trust Nginx to handle SSL and Host headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VerifiHireAI_backend.urls'

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

WSGI_APPLICATION = 'VerifiHireAI_backend.wsgi.application'
ASGI_APPLICATION = 'VerifiHireAI_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            # Since Redis is in Docker but exposed to 6379, 127.0.0.1 works for local backend
           "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = f"redis://{os.environ.get('REDIS_HOST', '127.0.0.1')}:{os.environ.get('REDIS_PORT', 6379)}/0"
CELERY_RESULT_BACKEND = f"redis://{os.environ.get('REDIS_HOST', '127.0.0.1')}:{os.environ.get('REDIS_PORT', 6379)}/0"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-reservations-every-minute': {
        'task': 'api.tasks.cleanup_expired_reservations_task',
        'schedule': crontab(minute='*'),
    },
}


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_CONNECT_TIMEOUT = int(os.environ.get('DB_CONNECT_TIMEOUT', '10'))
DB_SSLMODE = os.environ.get('DB_SSLMODE', '').strip().lower()

db_options = {}
if DB_SSLMODE:
    db_options['sslmode'] = DB_SSLMODE
    db_options['connect_timeout'] = DB_CONNECT_TIMEOUT

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'verifihireai'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '12345'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        **({'OPTIONS': db_options} if db_options else {}),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/django-static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# File upload limits (2.5MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440

# OTP settings
EMAIL_OTP_EXPIRY_SECONDS = 120

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

default_cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "https://www.verifihireai.com",
    "http://20.205.31.46",
]

CORS_ALLOW_ALL_ORIGINS = True
CSRF_ALLOW_WILD_CARD_HOST = True

CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS", default_cors_origins)

CORS_ALLOW_CREDENTIALS = True

# Allow all methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Allow all headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF settings for API
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", default_cors_origins)

# CSRF cookie settings
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True  # Enforce HTTPS
CSRF_USE_SESSIONS = False

# Session cookie settings
SESSION_COOKIE_SECURE = True # Enforce HTTPS

# Email Configuration for Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'python.nexnoratech@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'aazm gwze vplo kehg')
DEFAULT_FROM_EMAIL = f"VerifiHire AI <{EMAIL_HOST_USER}>"
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')
ASSEMBLYAI_API_KEY = os.environ.get('ASSEMBLYAI_API_KEY')

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
