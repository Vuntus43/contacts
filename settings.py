import os

APP_SETTINGS = None

ADMINS = (('img', 'img@it-solution.ru'),)

BASE_DOMAIN = ''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.dirname(__file__).replace('\\','/')


SECRET_KEY = 'br_)_gosz)tuok5m$31*b42bu6mj##vaoa9tuhr66^g$-sotye'

DEBUG = True
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://c5b354d95473.ngrok-free.app',
    'https://*.bitrix24.ru',
]
SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True  # True, если будешь на https
CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',

    'integration_utils.bitrix24',
    'integration_utils.its_utils.app_gitpull',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # XFrameOptionsMiddleware не используем
]

ROOT_URLCONF = 'urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'wsgi.application'


DATABASES = {}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
ENTRY_FILE_UPLOADING_FOLDER = os.path.join(MEDIA_ROOT, 'uploaded_entrie_files')

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]

try:
    from integration_utils.its_utils.mute_logger import MuteLogger
    ilogger = MuteLogger()
except Exception:
    ilogger = None

try:
    from local_settings import *  # здесь зададим APP_SETTINGS и B24_WEBHOOK
except ImportError:
    from warnings import warn
    warn('create local_settings.py')

if not APP_SETTINGS:
    from integration_utils.bitrix24.local_settings_class import LocalSettingsClass
    APP_SETTINGS = LocalSettingsClass(
        app_domain='',                 # локально пусто
        app_name='map',     # наше имя
        salt='dev_salt',               # любые dev-значения
        secret_key='dev_secret',
        application_index_path='/',
    )

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
