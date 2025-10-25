from pathlib import Path
import os

# ============================================================
# BASE & DIRETÓRIOS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "lab/static"
MEDIA_DIR = BASE_DIR / "mediafiles"

# ============================================================
# CONFIGURAÇÃO BÁSICA
# ============================================================
SECRET_KEY = 'django-insecure--000pddcet2g+a32av-$59gyew5h-k77g1*(s81u3dyah$g%!p'
DEBUG = True
ALLOWED_HOSTS = []

# ============================================================
# APPS
# ============================================================
INSTALLED_APPS = [
    # UI/Admin
    'jazzmin',

    # Apps internas
    'lab',
    'phonenumber_field',
    'django_countries',

    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================================
# URLS E WSGI
# ============================================================
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# ============================================================
# DATABASE
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ============================================================
# PASSWORD VALIDATORS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ============================================================
# INTERNACIONALIZAÇÃO
# ============================================================
LANGUAGE_CODE = 'pt-MZ'
TIME_ZONE = 'Africa/Maputo'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ============================================================
# STATIC & MEDIA
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [STATIC_DIR]

MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR

# ============================================================
# DJANGO DEFAULTS
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CONFIGURAÇÕES DE TERCEIROS
# ============================================================
PHONENUMBER_DEFAULT_REGION = "MZ"

# ============================================================
# JAZZMIN
# ============================================================
JAZZMIN_SETTINGS = {
    "site_title": "SYS-LAB",
    "site_header": "SYS-LAB Admin",
    "welcome_sign": "Sys-G-Lab - Sistema de Gestão Laboratorial",
    "site_logo": "img/logo.png",          # relativo a STATICFILES_DIRS
    "custom_css": "css/admin_custom.css", # relativo a STATICFILES_DIRS
    "show_sidebar": True,
    "navigation_expanded": True,
}

# ============================================================
# ADMIN LOGO EXTRA
# ============================================================
ADMIN_LOGO = os.path.join(STATIC_URL, "img/logo.png")

# ============================================================
# AJUSTES OPCIONAIS DE SEGURANÇA (aprimoramento)
# ============================================================
CSRF_COOKIE_SECURE = False if DEBUG else True
SESSION_COOKIE_SECURE = False if DEBUG else True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ============================================================
# PATHS DE TEMPLATES
# ============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True