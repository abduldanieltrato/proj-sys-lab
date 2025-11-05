
"""
AnaLinkLab - Configurações Principais do Projeto Django
Autor: Abdul Daniel Trato
Data: 2025
"""

from pathlib import Path
import os
import random

# ============================================================
# 📍 BASE
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# 🔐 SEGURANÇA
# ============================================================
SECRET_KEY = "coloque_aqui_uma_chave_super_segura_e_unica"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ============================================================
# 🌐 INTERNACIONALIZAÇÃO
# ============================================================
LANGUAGE_CODE = "pt-MZ"
TIME_ZONE = "Africa/Maputo"
USE_I18N = True
USE_TZ = True  # USE_L10N está deprecated, removido

# ============================================================
# 🗄️ BANCO DE DADOS
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

STATICFILES_DIRS = [BASE_DIR / "lab" / "static"]  # Certifique-se de criar esta pasta

# ============================================================
# ⚙️ APLICAÇÕES
# ============================================================
INSTALLED_APPS = [
    # UI/Admin
    "jazzmin",

    # App principal
    "lab",

    # Terceiros
    "phonenumber_field",
    "django_countries",
    "django_extensions",

    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]


# ============================================================
# 📧 EMAIL (SMTP)
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "abdultrato@gmail.com"
EMAIL_HOST_PASSWORD = "CfCw@6205"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# ============================================================
# 🧩 MIDDLEWARE
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

ROOT_URLCONF = "backend.urls"
WSGI_APPLICATION = "backend.wsgi.application"

# ============================================================
# 🔑 AUTENTICAÇÃO
# ============================================================
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

# ============================================================
# 🔒 SEGURANÇA HTTP
# ============================================================
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# ============================================================
# 🧾 VALIDAÇÃO DE SENHAS
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================================
# 📧 EMAIL (SMTP)
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "abdultrato@gmail.com"
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD", "CfCw@6205")  # Sugestão: usar env
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ============================================================
# 🧠 CACHE
# ============================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "analinklab-cache",
    }
}

# ============================================================
# 🧾 LOGGING
# ============================================================
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "django.log"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name} — {message}", "style": "{"},
    },
    "handlers": {
        "file": {"level": "INFO", "class": "logging.FileHandler", "filename": str(LOG_FILE), "formatter": "verbose"},
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "loggers": {"django": {"handlers": ["file", "console"], "level": "INFO", "propagate": True}},
}

# ============================================================
# 🧱 DJANGO DEFAULTS
# ============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# 🧩 TEMPLATES
# ============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

# ============================================================
# 🕓 SESSÕES
# ============================================================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_NAME = "analinklab_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 30 * 60  # 30 minutos

# ============================================================
# 🎨 JAZZMIN SETTINGS — AnaLinkLab
# ============================================================
JAZZMIN_SETTINGS = {
    "site_title": "AnaLinkLab | Painel Administrativo",
    "site_header": "AnaLinkLab | Gestão de Análises Clínicas",
    "site_brand": " ",
    "welcome_sign": "Bem-vindo ao AnaLinkLab",
    "site_logo": "img/ana_link_lab_logo.png",
    "login_logo": "img/ana_link_lab_logo.png",
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_custom.js",
    "copyright": "AnaLinkLab Systems",
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "lab"],
    "icons": {
        "lab": "fas fa-vials",
        "lab.Requisicao": "fas fa-vials",
		"lab.Resultado": "fas fa-microscope",
		"lab.Paciente": "fas fa-user-injured",
        "auth": "fas fa-users-cog",
        "auth.User": "fas fa-user-shield",
        "default_icon_parents": "fas fa-folder-open",
        "default_icon_children": "fas fa-file-medical",
        "theme":  "sandstone",
        "search_model": "auth.User",
        "changeform_format": "horizontal_tabs",
    }

}

JAZZMIN_UI_TWEAKS = {
    "custom_css": "css/admin_custom.css",
    "theme": "cosmo",
    "navbar": "navbar-white navbar-light",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "brand_color": "navbar-primary",
    "actions_sticky_top": True,
    "sidebar_nav_child_indent": True,
    "related_modal_active": True,
    "layout_fixed_navbar": True,
    "layout_fixed_sidebar": True,
    "layout_boxed": False,
    "layout_collapsed_sidebar": False,
    "layout_compact_sidebar": True,
    "no_navbar_border": True,
    "custom_css": "css/custom.css",
}
