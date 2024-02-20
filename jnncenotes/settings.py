"""
Django settings for jnncenotes project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-zj6)sll(z$5hzsl5(q9!&cd#bsv0vgm95y=@0%&d432g0)gyu!"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# VARIABLES FOR AZURE STORAGE
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT")
AZURE_VAULT_ACCOUNT = os.environ.get("AZURE_VAULT_ACCOUNT")
AZURE_STORAGE_KEY_NAME = os.environ.get("AZURE_STORAGE_KEY_NAME")
AZURE_APP_BLOB_NAME = os.environ.get("AZURE_APP_BLOB_NAME")

# Constants
WEBSITE_NAME = os.environ.get("WEBSITE_NAME")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL")

# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_ID') 
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PW')

# django-verify-email
DEFAULT_FROM_EMAIL = 'Learn Easy<noreply@learneasy.study>'
EXPIRE_AFTER = "1d"
HTML_MESSAGE_TEMPLATE = 'notes/verification/html_message_template.html'
REQUEST_NEW_EMAIL_TEMPLATE = 'notes/verification/request_new_email.html'
SUBJECT = "Verify your email address"

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # django-allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    'allauth.socialaccount.providers.google',

    "notes.apps.NotesConfig",
    "rest_framework",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # django-allauth
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "jnncenotes.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                "notes.context_processors.constants",
            ],
        },
    },
]

WSGI_APPLICATION = "jnncenotes.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'notes:home'

# django-allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_FORMS = {
    'login': 'notes.forms.CustomLoginForm',
    'signup': 'notes.forms.CustomSignUpForm',
    'reauthenticate': 'notes.forms.CustomReauthenticateForm',
    'reset_password': 'notes.forms.CustomResetPasswordForm',
    'add_email': 'notes.forms.CustomAddEmailForm',
    'set_password': 'notes.forms.CustomSetPasswordForm',

}

# ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_ADAPTER = 'notes.account_adapter.CustomAccountAdapter'

ALLOW_SIGN_UP = os.environ.get("ALLOW_SIGN_UP", "True") == "True"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "VERIFIED_EMAIL": True,
    }
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
# SOCIALACCOUNT_LOGIN_ON_GET = True