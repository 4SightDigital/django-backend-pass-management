import os
import dj_database_url
from pathlib import Path
from datetime import timedelta
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# SECURITY (Development)
# ======================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = True

# Allow all hosts for development
ALLOWED_HOSTS = ["*"]

# Allow frontend to POST without CSRF issues
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000",           # React dev server (optional, for local development)
    "http://127.0.0.1:3000",           # React dev server (optional)
    "https://pass1432.vercel.app", ]

# ======================
# APPLICATIONS
# ======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local app
    'app',

    # API
    'rest_framework',
    'drf_spectacular',

    # CORS
    'corsheaders',
]

# ======================
# REST FRAMEWORK
# ======================
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # Allow all requests in development
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ticket Management API',
    'DESCRIPTION': 'API documentation for React frontend',
    'VERSION': '1.0.0',
}

# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS config
CORS_ALLOW_HEADERS = list(default_headers) + ["authorization"]
CORS_ALLOW_ALL_ORIGINS = True

# ======================
# URLS & TEMPLATES
# ======================
ROOT_URLCONF = 'ticket_system.urls'

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

WSGI_APPLICATION = 'ticket_system.wsgi.application'

# ======================
# DATABASE (Dev-friendly)
# ======================
DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=False  # Turn off SSL for dev
    )
}

# ======================
# PASSWORD VALIDATION
# ======================
AUTH_PASSWORD_VALIDATORS = []

# ======================
# INTERNATIONALIZATION
# ======================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ======================
# STATIC FILES
# ======================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ======================
# DEFAULT AUTO FIELD
# ======================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================
# AUTH REDIRECTS
# ======================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = 'dashboard_view'
LOGOUT_REDIRECT_URL = '/login/'
