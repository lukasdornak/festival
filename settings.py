import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.environ.get('SECRET_KEY', 'not secret key')

DEBUG = False

ADMINS = [('Lukáš Dorňák', 'lukasdornak@gmail.com')]

MANAGERS = ADMINS

ALLOWED_HOSTS = ['festivalkratasy.cz', 'www.festivalkratasy.cz', 'festivalkratasy.com', 'www.festivalkratasy.com']

INSTALLED_APPS = [
    'festival',
    'ckeditor',
    'imagekit',
    'import_export',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'festival.middleware.FestivalLocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'festival/locale'),
)

ROOT_URLCONF = 'festival.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.i18n',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'data/db.sqlite3'),
    }
}

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

LANGUAGES = (
    ('en', 'English'),
    ('cs', 'Czech'),
)

LANGUAGE_CODE = 'cs'

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Styles', 'Format' 'FontSize', 'Bold', 'Italic', 'Underline', 'Strike', 'RemoveFormat', 'PasteText', 'Redo', 'Undo',
             'Link', 'Unlink', 'Anchor'],
            ['NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar'],
            ['TextColor', 'BGColor'],
            ['Source'],
        ]
    }
}

LOGIN_URL = '/admin/login'

TP_MERCHANT_ID = os.environ.get('TP_MERCHANT_ID', 1)
TP_ACCOUNT_ID = os.environ.get('TP_ACCOUNT_ID', 1)
TP_PASSWORD = os.environ.get('TP_PASSWORD', 'my$up3rsecr3tp4$$word')
TP_GATE_URL = os.environ.get('TP_GATE_URL', 'https://www.thepay.cz/demo-gate/')
TP_DATA_API_PASWORD = os.environ.get('TP_DATA_API_PASWORD', 'my$up3rsecr3tp4$$word')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'email_host')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'email_host_user')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'email_host_password')
EMAIL_PORT = 25

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Styles', 'Format', 'FontSize', 'Bold', 'Italic', 'Underline', 'Strike', 'RemoveFormat', 'PasteText', 'Redo', 'Undo', 'Link', 'Unlink', 'Anchor'],
            ['NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar'],
            ['TextColor', 'BGColor'],
            ['Source'],
        ]
    }
}
