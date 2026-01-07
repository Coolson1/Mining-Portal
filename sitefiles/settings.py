# Django settings for the project.
import os
# os is used to construct file paths and interact with the environment.
from pathlib import Path
# Path provides an easy-to-use path API for filesystem paths.

# BASE_DIR is the root folder of the project (two levels up from this file).
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'replace-this-with-a-secure-key-for-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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

# Email settings: default to console backend for development. To send real emails
# Email settings: use console backend by default for development. If you set
# the environment variables `GMAIL_HOST_USER` and `GMAIL_APP_PASSWORD` the
# project will automatically use Gmail SMTP with the provided app password.
GMAIL_HOST_USER = os.environ.get('GMAIL_HOST_USER')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
if GMAIL_HOST_USER and GMAIL_APP_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = GMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = GMAIL_APP_PASSWORD
    DEFAULT_FROM_EMAIL = GMAIL_HOST_USER
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'no-reply@fourahbay.example'

# Warn if running in production mode but still using the console email backend
if not DEBUG and EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    import warnings
    warnings.warn(
        'DEBUG is False but EMAIL_BACKEND is console.EmailBackend.\n'
        'Emails will not be delivered to real addresses.\n'
        'Set GMAIL_HOST_USER and GMAIL_APP_PASSWORD in environment or configure a real SMTP backend for production.',
        RuntimeWarning
    )
