import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================
# 🔐 Основные настройки
# ==========================

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key")
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# JWT signing key
JWT_SECRET = os.getenv("JWT_SECRET")  # обязательно в .env в проде

# ==========================
# 🧩 Приложения
# ==========================

DJANGO_APPS = [
    'modeltranslation',
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

LOCAL_APPS = [
    'apps.user',
    'apps.product.apps.ProductConfig',
    'apps.favorite',
    'apps.cart',
    'apps.order',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ==========================
# ⚙️ Middleware
# ==========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'wear_and_go.middleware.QueryLangMiddleware',

    # CORS (должен идти до CommonMiddleware)
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wear_and_go.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # для фронта/админки
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wear_and_go.wsgi.application'


# ==========================
# 🗄️ База данных
# ==========================

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sway',
        'USER': 'sway_admin',
        'PASSWORD': 'sway_shop',
        'HOST': 'localhost',
        'PORT': '5433'
    }
}


# ==========================
# 🔑 Аутентификация / JWT
# ==========================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),

    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),

    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,

    'UPDATE_LAST_LOGIN': False,
}


AUTHENTICATION_BACKENDS = [
    'apps.user.backends.PhoneNumberBackend',
    'django.contrib.auth.backends.ModelBackend',  # оставляем на всякий случай
]

AUTH_USER_MODEL = 'user.User'  # кастомная модель


# ==========================
# 🌐 CORS (для фронта на Vite)
# ==========================

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


# ==========================
# 🌍 Локализация
# ==========================

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

LANGUAGES = (
    ('ru', 'Russian'),
    ('uz', 'Uzbek'),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'


# ==========================
# 🖼️ Статика и медиа
# ==========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==========================
# ⚙️ Прочее
# ==========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
