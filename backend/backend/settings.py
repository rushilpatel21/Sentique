from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "dummy-secret-key"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.usersessions",
    'drf_spectacular',
    'drf_yasg',
    'reviews',
    'django_extensions',
    'gemini_integration',
    'onboard',
    'dashboard',
    'corsheaders',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]


AUTH_USER_MODEL = 'onboard.CustomUser'



ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# SPECTACULAR_SETTINGS = {
#     'TITLE': 'Share Ease API',
#     'DESCRIPTION': 'API Docs to understand the Share Ease API',
#     'VERSION': '0.1.0',
#     'SERVE_INCLUDE_SCHEMA': False,
#     'SCHEMA_PATH_PREFIX': "/_allauth/api/",
#     'SCHEMA_COERCE_PATH_PK_SUFFIX': False,
# }
SPECTACULAR_SETTINGS = {
    "EXTERNAL_DOCS": {"description": "allauth", "url": "/_allauth/openapi.html"},
}


WSGI_APPLICATION = "backend.wsgi.application"


# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vector',
        'USER': 'rushilpatel',
        'PASSWORD': "",
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

ALLOWED_HOSTS = ["localhost","localhost:5173","127.0.0.1:8000" , "127.0.0.1"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]

ACCOUNT_ADAPTER = 'onboard.adapters.AccountAdapter'
HEADLESS_ADAPTER = 'onboard.adapters.CustomHeadlessAdapter'


# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/1'  # Redis as broker
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'  # Store task results
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTHENTICATION_BACKENDS = ("allauth.account.auth_backends.AuthenticationBackend",)

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*']
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_LOGIN_BY_CODE_ENABLED = False
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = False

HEADLESS_ONLY = True

HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "/account/verify-email/{key}",
    "account_reset_password": "/account/password/reset",
    "account_reset_password_from_key": "/account/password/reset/key/{key}",
    "account_signup": "/account/signup",
    "socialaccount_login_error": "/account/provider/callback",
}
HEADLESS_SERVE_SPECIFICATION = True


# Add these CORS settings at the end of the file
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Your frontend development server
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

try:
    from .local_settings import *  # noqa
except ImportError:
    pass