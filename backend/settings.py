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
# 🔐 SEGURANÇA BÁSICA APRIMORADA
# ============================================================

# Chave secreta – deve ser única e complexa em produção
SECRET_KEY = "coloque2541SDDFSdhgnmvyeetga_uma_chave_fnd<hsudchsuper_complexa_aquihdhfwysyd"

# Desativa debug em produção
DEBUG = True

# Hosts permitidos para evitar Host Header attacks
ALLOWED_HOSTS = [
	"127.0.0.1",
	"localhost",
]


# ============================================================
# 🌐 INTERNACIONALIZAÇÃO APRIMORADA
# ============================================================

# Idioma padrão
LANGUAGE_CODE = "pt-MZ"

# Fuso horário
TIME_ZONE = "Africa/Maputo"

# Internacionalização e formatação de datas/números
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ============================================================
# 📡 BANCO DE DADOS (SQLite)
# ============================================================
DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.sqlite3",
		"NAME": BASE_DIR / "db.sqlite3",
	}
}

# ============================================================
# 📁 STATIC & MEDIA APRIMORADO
# ============================================================

# URLs públicas
STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Diretórios onde os arquivos serão coletados
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# Diretórios adicionais de arquivos estáticos
STATICFILES_DIRS = [
	BASE_DIR / "lab" / "static"
]

# Configurações adicionais recomendadas
# Gzip e cache headers podem ser configurados no servidor (nginx/Apache)
# para melhorar a performance na entrega de arquivos estáticos.

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
# SEGURANÇA HTTP APRIMORADA
# ============================================================

# Garante que os cookies de sessão e CSRF só sejam enviados via HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Redireciona automaticamente todas requisições HTTP para HTTPS
SECURE_SSL_REDIRECT = True

# Protege contra Clickjacking
X_FRAME_OPTIONS = "DENY"

# HSTS – força navegadores a acessarem via HTTPS por um período
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Evita que o navegador interprete arquivos como HTML quando não deveriam
SECURE_CONTENT_TYPE_NOSNIFF = True

# Protege contra ataques de XSS
SECURE_BROWSER_XSS_FILTER = True


# ============================================================
# AUTENTICAÇÃO
# ============================================================
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"

# ============================================================
# 📧 CONFIGURAÇÃO DE EMAIL (SMTP GMAIL)
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "abdultrato@gmail.com"
EMAIL_HOST_PASSWORD = "CfCw@6205"
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
# 🧾 LOGGING
# ============================================================
import os

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "django.log"

LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,

	"formatters": {
		"verbose": {
			"format": "[{asctime}] {levelname} {name} — {message}",
			"style": "{",
		},
	},

	"handlers": {
		"file": {
			"level": "INFO",
			"class": "logging.FileHandler",
			"filename": str(LOG_FILE),
			"formatter": "verbose",
		},
		"console": {
			"level": "INFO",
			"class": "logging.StreamHandler",
			"formatter": "verbose",
		},
	},

	"loggers": {
		"django": {
			"handlers": ["file", "console"],
			"level": "INFO",
			"propagate": True,
		},
	},
}

# ============================================================
# 🎨 ADMIN PERSONALIZAÇÃO (BioLink)
# ============================================================
JAZZMIN_SETTINGS = {
	"site_title": "BioLink | Painel Administrativo",
	"site_header": "BioLink Admin",
	"welcome_sign": "Bem-vindo ao BioLink — Sistema de Gestão Laboratorial",
	"site_logo": "img/biolink_logo.png",
	"login_logo": "img/biolink_logo.png",
	"login_logo_dark": None,
	"custom_css": "css/admin_custom.css",
	"custom_js": None,
	"show_sidebar": True,
	"navigation_expanded": True,
	"site_brand": "BioLink",
	"copyright": "© 2025 BioLink Systems",
	"topmenu_links": [
		{"name": "Início", "url": "admin:index", "permissions": ["auth.view_user"]},
		{"app": "lab"},
		{"app": "pacientes"},
		{"app": "doacoes"},
	],
	"use_google_fonts_cdn": True,
	"related_modal_active": True,
	"icons": {
		"auth": "fas fa-users-cog",
		"lab": "fas fa-vials",
		"pacientes": "fas fa-user-injured",
		"doacoes": "fas fa-hand-holding-medical",
		"transfusoes": "fas fa-syringe",
	},
	"changeform_format": "horizontal_tabs",
	"language_chooser": True,
}


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

# ============================================================
# LOG DIR AUTO-CREATE
# ============================================================
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
(LOGS_DIR / "django.log").touch(exist_ok=True)
