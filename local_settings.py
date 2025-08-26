DEBUG = True
ALLOWED_HOSTS = ['*']

from integration_utils.bitrix24.local_settings_class import LocalSettingsClass

APP_SETTINGS = LocalSettingsClass(
    portal_domain='b24-q0k90e.bitrix24.ru',
    app_domain='127.0.0.1:8000',
    app_name='contacts',   # имя под наш проект
    salt='dev_salt_change_me',
    secret_key='dev_secret_change_me',
    application_bitrix_client_id='local.68adca545b20c0.25503454',   # из карточки "Локальное приложение"
    application_bitrix_client_secret='jFskhW2GZtnfvb96PeatQBgXQnPzx4LGcBPQvMQdCPEj2BYVxA',  # секрет оттуда же
    application_index_path='/',
)

DOMAIN = 'http://127.0.0.1:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'companies_map',
        'USER': 'companies_user',
        'PASSWORD': 'companiesuserpass',   # твой пароль
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}

