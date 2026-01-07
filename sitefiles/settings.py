# Django settings for the project.
import os
"""os is used to access environment variables and construct paths."""
from pathlib import Path
"""Path provides an easy-to-use path API for filesystem paths."""
# Try to load a local .env file when present (development convenience).
try:
    # Import here so prod systems without python-dotenv won't fail unless they rely on .env
    from dotenv import load_dotenv  # type: ignore
    # Load .env from project root if present, but do not override existing env vars.
    BASE_DIR = Path(__file__).resolve().parent.parent
    load_dotenv(BASE_DIR / '.env', override=False)
except Exception:
    # If python-dotenv isn't installed or .env doesn't exist, continue silently.
    pass

# BASE_DIR is the root folder of the project (two levels up from this file).
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'replace-this-with-a-secure-key-for-production'

# SECURITY WARNING: don't run with debug turned on in production!
# Allow overriding DEBUG with an environment variable. Defaults to True for development.
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('1', 'true', 'yes')

# Hosts allowed to serve the project; in development this can be empty or localhost.
ALLOWED_HOSTS = ['*']

# Application definition: installed apps include Django defaults and our 'files' app.
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'files.apps.FilesConfig',
]

# Middleware processes requests/responses; keep Django defaults for now.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration points to sitefiles.urls below.
ROOT_URLCONF = 'sitefiles.urls'

# Templates configuration tells Django where to find HTML templates.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# WSGI application path for deployment servers.
WSGI_APPLICATION = 'sitefiles.wsgi.application'

# Database configuration: using SQLite for simplicity.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation using Django's default validators (kept simple here).
AUTH_PASSWORD_VALIDATORS = []

# Internationalization settings.
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# Additional directories to look for static files during development.
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / "staticfiles" # new

# Media files (user uploaded files) settings.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration: choose backend based on environment variables.
# Priority order:
# 1) If GMAIL_HOST_USER and GMAIL_APP_PASSWORD are set, use Gmail SMTP.
# 2) If USE_LOCAL_SMTP is truthy, point SMTP to a local server (MailHog on 1025).
# 3) Otherwise fall back to console backend (development friendly; does not send email).


    # Configure Gmail SMTP using supplied credentials (recommended for production).
   
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = 'abdul1ck2@gmail.com'
    EMAIL_HOST_PASSWORD = 'tftuebhxwsqvvecx'
    DEFAULT_FROM_EMAIL = 'abdul1ck2@gmail.com'
