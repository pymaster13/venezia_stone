"""
Django settings for VeneziaStone project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '****************************************'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

CORS_ORIGIN_ALLOW_ALL = True
AUTH_USER_MODEL = "Account.User"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'djoser',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'rest_auth.registration',
    'Account',
    'phonenumber_field',
    'celery',
    'View1C',
    'kronos',
]

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

ROOT_URLCONF = 'VeneziaStone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'VeneziaStone.wsgi.application'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
   'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}



# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         # 'NAME': 'venezia_db',
#         # 'USER' : 'django_admin',
#         # 'PASSWORD' : 'c4',
#         # 'HOST' : '127.0.0.1',
#         # 'PORT' : '5432',
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'venezia_stone', #NAME OF DATABASE
        'USER': 'root', #NAME OF USER
        'PASSWORD': 'veneziastone', # USER PASSWORD
        'HOST': '',
        'PORT': '',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ' '
EMAIL_HOST_PASSWORD = ' '

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

DJOSER = {
    'ACTIVATION_URL': '#/account/activate/{uid}/{token}',
    'PASSWORD_RESET_CONFIRM_URL' : '#/account/password/reset/confirm/{uid}/{token}',
    'PASSWORD_RESET_CONFIRM_RETYPE' : True,
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL' : True,
    'SERIALIZERS': {
    'user_create' : 'Account.views.UserCreateSerializer',
    },

    'USER_CREATE_PASSWORD_RETYPE' : False,
    'EMAIL':{
    "password_reset": "Account.views.PasswordResetEmail",
    "activation": "Account.views.ActivationEmail",
    "confirmation": "Account.views.ConfirmationEmail",
    },

    'PERMISSIONS':{
    'user': ['rest_framework.permissions.AllowAny'],
    'user_create': ['rest_framework.permissions.AllowAny'],
    'activation': ['rest_framework.permissions.AllowAny'],
    'password_reset': ['rest_framework.permissions.AllowAny'],
    'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
    }

}

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
 "django.contrib.auth.backends.ModelBackend",
 "allauth.account.auth_backends.AuthenticationBackend",
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# ???????????????? url ?????? ???????????????????? ????????????????????????
MEDIA_URL = '/media/'
# ???????? ???????????????? ????????????????
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

SENDSMS_FROM_NUMBER = ''
SENDSMS_ACCOUNT_SID = ''
SENDSMS_AUTH_TOKEN = ''

PHONE_LOGIN_ATTEMPTS = 10
PHONE_LOGIN_OTP_LENGTH = 6
PHONE_LOGIN_OTP_HASH_ALGORITHM = 'sha256'

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}