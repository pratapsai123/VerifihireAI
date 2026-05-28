"""
Django settings for VerifiHireAI_backend project. # Reload trigger
"""


import os
from pathlib import Path
from decouple import config, Csv
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-change-this-in-production-12345")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())

FRONTEND_BASE_URL = config("FRONTEND_BASE_URL", default="https://verifihireai.com")


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
    'deepface_proctoring',
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
    'ai_candidates.middleware.InterviewRateLimitMiddleware',
    'ai_candidates.middleware.InterviewQueueMiddleware',
    'ai_candidates.middleware.InterviewHealthCheckMiddleware',
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
CELERY_BROKER_URL = f"redis://{config('REDIS_HOST', default='127.0.0.1')}:{config('REDIS_PORT', default=6379, cast=int)}/0"
CELERY_RESULT_BACKEND = f"redis://{config('REDIS_HOST', default='127.0.0.1')}:{config('REDIS_PORT', default=6379, cast=int)}/0"
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
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'CONN_MAX_AGE': 0,  # Set to 0 to close connection at the end of each request
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
        'api.authentication.DBContextJWTAuthentication',

    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=12),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

default_cors_origins = [
    "https://verifihireai.com",
    "https://verifihireai.com",
    "https://verifihireai.com",
    "https://verifihireai.com",
    "https://verifihireai.com",
    "http://20.205.31.46",
    "https://verifihireai.com",
]

CORS_ALLOW_ALL_ORIGINS = True
CSRF_ALLOW_WILD_CARD_HOST = True

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default=",".join(default_cors_origins), cast=Csv())

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
    'x-session-id',
]

# CSRF settings for API
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default=",".join(default_cors_origins), cast=Csv())

# CSRF cookie settings
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = True  # Enforce HTTPS
CSRF_USE_SESSIONS = False

# Session cookie settings
SESSION_COOKIE_SECURE = True # Enforce HTTPS

# Email Configuration for Gmail SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='python.nexnoratech@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = f"VerifiHire AI <{EMAIL_HOST_USER}>"
DEEPSEEK_BASE_URL = config('DEEPSEEK_BASE_URL', default='https://api.deepseek.com')
DEEPSEEK_MODEL = config('DEEPSEEK_MODEL', default='deepseek-v4-flash')
DEEPSEEK_API_KEYS = [
    config('DEEPSEEK_API_KEY_1', default='sk-6535c0f5ed654ee1a48ebf2a08efa1cd'),
    # Add more keys for rotation / higher concurrency:
    # config('DEEPSEEK_API_KEY_2', default=''),
    # config('DEEPSEEK_API_KEY_3', default=''),
]
# Remove empty/placeholder keys
DEEPSEEK_API_KEYS = [k for k in DEEPSEEK_API_KEYS if k and k != 'your-deepseek-api-key-here']
# Legacy aliases so existing references don't break during migration
DEEPSEEK_API_KEY = DEEPSEEK_API_KEYS[0] if DEEPSEEK_API_KEYS else None

# ── GROQ Keys for Resume Screening Fallback ──
GROQ_API_KEYS = [
    config('GROQ_API_KEY_1', default=''),
    config('GROQ_API_KEY_2', default=''),
    config('GROQ_API_KEY_3', default=''),
]
# Remove empty/placeholder keys
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]
GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else None

ASSEMBLYAI_API_KEY = config('ASSEMBLYAI_API_KEY', default=None)

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

SECURITY_SIGNATURE_RULES = [
    {
        "label": "AnyDesk",
        "signatures": ["anydesk", "ad_svc", "ad.tray"],
        "pathSignatures": ["anydesk.exe", "/anydesk", "com.philandro.anydesk", "philandro"],
        "serviceProcesses": ["anydesk service"],
        "activeIndicators": {
            "listenPorts": [7070],
            "activeConnectionKeywords": ["anydesk"],
            "windowTitles": ["anydesk"],
        },
    },
    {
        "label": "TeamViewer",
        "signatures": ["teamviewer", "teamviewer_desktop", "teamviewer_host", "tv_w32"],
        "pathSignatures": ["teamviewer.exe", "/teamviewer", "com.teamviewer", "teamviewerhost"],
        "serviceProcesses": ["teamviewer_service.exe"],
        "activeIndicators": {
            "listenPorts": [5938],
            "activeConnectionKeywords": ["teamviewer"],
            "windowTitles": ["teamviewer"],
        },
    },
    {
        "label": "UltraViewer",
        "signatures": ["ultraviewer", "ultraviewer_desktop", "ultraviewer_service"],
        "pathSignatures": ["ultraviewer.exe", "/ultraviewer"],
        "serviceProcesses": [],
        "activeIndicators": {
            "listenPorts": [],
            "activeConnectionKeywords": ["ultraviewer"],
            "windowTitles": ["ultraviewer"],
        },
    },
    {
        "label": "Chrome Remote Desktop",
        "signatures": ["remoting_host", "chromoting"],
        "pathSignatures": ["remoting_host.exe", "/chrome-remote-desktop", "chromoting"],
        "serviceProcesses": [],
        "activeIndicators": {
            "listenPorts": [],
            "activeConnectionKeywords": ["remoting_host", "chromoting"],
            "windowTitles": ["chrome remote desktop"],
        },
    },
    {
        "label": "RustDesk",
        "signatures": ["rustdesk"],
        "pathSignatures": ["rustdesk.exe", "/rustdesk"],
        "serviceProcesses": [],
        "activeIndicators": {
            "windowTitles": ["rustdesk"],
        },
    },
]
