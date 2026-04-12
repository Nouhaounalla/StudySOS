from pathlib import Path
from dotenv import load_dotenv
import os
from os import getenv

load_dotenv()  # Load .env file

from datetime import timedelta
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.ProfileCompletionMiddleware',
]
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ SECURITY
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')

# ✅ APPS
INSTALLED_APPS = [
    'daphne',  # Must be FIRST
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # ADD THIS for logout
    'corsheaders',
    'users',
]

# ✅ Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# ✅ CORS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

ROOT_URLCONF = 'studysos.urls'

# ✅ TEMPLATES
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
                'users.context_processors.jwt_user',
            ],
        },

    },
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']


WSGI_APPLICATION = 'studysos.wsgi.application'

# ✅ ✅ ✅ SUPABASE DATABASE (PostgreSQL)
from os import getenv

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('PGDATABASE'),
        'USER': getenv('PGUSER'),
        'PASSWORD': getenv('PGPASSWORD'),
        'HOST': getenv('PGHOST'),
        'PORT': getenv('PGPORT', 5432),
        'OPTIONS': { 
            'sslmode': 'require',
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30s query timeout
        },
        'DISABLE_SERVER_SIDE_CURSORS': True,
        'CONN_HEALTH_CHECKS': True,
        'CONN_MAX_AGE': 600,  # Keep connections alive for 10 minutes
        'ATOMIC_REQUESTS': True,  # Wrap each request in transaction
    }
}

# Connection pooling for production (optional but recommended)
if not DEBUG:
    DATABASES['default']['OPTIONS']['options'] += ' -c idle_in_transaction_session_timeout=60000'

# ✅ Custom User Model
AUTH_USER_MODEL = 'users.User'

# ✅ Locale
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Tunis'
USE_I18N = True
USE_TZ = True

# ✅ Static / Media
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Short-lived
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # Longer-lived
    'ROTATE_REFRESH_TOKENS': True,                     # Security feature
    'BLACKLIST_AFTER_ROTATION': True,                  # Invalidate old refresh tokens
    'UPDATE_LAST_LOGIN': True,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    
    # Cookie settings (custom - we'll implement these)
    'AUTH_COOKIE': 'access_token',           # Name of access token cookie
    'AUTH_COOKIE_REFRESH': 'refresh_token',  # Name of refresh token cookie
    'AUTH_COOKIE_SECURE': True,              # HTTPS only in production
    'AUTH_COOKIE_HTTP_ONLY': True,           # Prevent JavaScript access
    'AUTH_COOKIE_SAME_SITE': 'Lax',          # CSRF protection
    'AUTH_COOKIE_PATH': '/',                 # Cookie available site-wide
}

# CORS Configuration for Cookies
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    # Add your production domain here
]
CORS_ALLOW_CREDENTIALS = True  # CRITICAL: Allows cookies to be sent

# Security Headers
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Must be False so JS can read it
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'

INSTALLED_APPS += ['channels', 'chat',]

ASGI_APPLICATION = 'studysos.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

