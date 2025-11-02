from datetime import date
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils import timezone
from pathlib import Path
import os

# ============================================================
# BASE
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# 🔐 SEGURANÇA BÁSICA
# ============================================================
SECRET_KEY = "chave-secreta-aqui-hdb78jds93almxddbwFDGVTRCgvshbhds"  # 🔒 substitui por uma chave segura
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ============================================================
# 🌐 INTERNACIONALIZAÇÃO
# ============================================================
LANGUAGE_CODE = "pt-MZ"
TIME_ZONE = "Africa/Maputo"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ============================================================
# 📡 BANCO DE DADOS
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ============================================================
# 📁 STATIC & MEDIA
# ============================================================
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "mediafiles"
STATICFILES_DIRS = [BASE_DIR / "lab" / "static"]

# ============================================================
# APPS
# ============================================================
INSTALLED_APPS = [
    # UI/Admin
    "jazzmin",

    # Apps internas
    "lab",

    # Terceiros
    "phonenumber_field",
    "django_countries",

    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# ============================================================
# URLS E WSGI
# ============================================================
ROOT_URLCONF = "backend.urls"
WSGI_APPLICATION = "backend.wsgi.application"

# ============================================================
# PASSWORD VALIDATORS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================================
# SEGURANÇA HTTP
# ============================================================
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
X_FRAME_OPTIONS = "SAMEORIGIN"

# ============================================================
# AUTENTICAÇÃO
# ============================================================
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

# ============================================================
# E-MAIL
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "teu_email@gmail.com"
EMAIL_HOST_PASSWORD = "tua_senha_aqui"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ============================================================
# CACHE
# ============================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# ============================================================
# LOGGING
# ============================================================
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "django.log"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name} — {message}", "style": "{"},
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": str(LOG_FILE),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["file"], "level": "INFO", "propagate": True},
    },
}

# ============================================================
# ADMIN PERSONALIZAÇÃO
# ============================================================
JAZZMIN_SETTINGS = {
    "site_title": "SYS-LAB",
    "site_header": "SYS-LAB Admin",
    "welcome_sign": "Sys-G-Lab - Sistema de Gestão Laboratorial",
    "site_logo": "img/logo.png",
    "custom_css": "css/admin_custom.css",
    "show_sidebar": True,
    "navigation_expanded": True,
}

# ============================================================
# CORS
# ============================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ============================================================
# DJANGO DEFAULTS
# ============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# TEMPLATES
# ============================================================
TEMPLATES_DIR = BASE_DIR / "templates"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
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
