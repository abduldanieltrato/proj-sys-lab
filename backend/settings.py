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
# 🎨 ADMIN PERSONALIZAÇÃO — AnaLinkLab
# ============================================================

JAZZMIN_SETTINGS = {
	# === Identidade visual ===
	"site_title": "AnaLinkLab | Painel Administrativo",
	"site_header": "AnaLinkLab Admin",
	"site_brand": "AnaLinkLab",
	"welcome_sign": "Bem-vindo ao AnaLinkLab",
	"site_logo": "img/ana_link_lab_logo.png",
	"login_logo": "img/ana_link_lab_logo.png",
	"copyright": " AnaLinkLab Systems",

	# === Layout e UX ===
	"show_sidebar": True,
    "show_jazzmin_version": False,
	"navigation_expanded": True, # Menu lateral expandido por padrão
	"hide_apps": [],
	"hide_models": [],
	"order_with_respect_to": ["auth", "lab"], # Ordem dos apps
	"custom_order": {
		"auth": 1,	
		"lab": 2, 
	},
	"search_url": "",	# URL de busca personalizada
	"use_google_fonts_cdn": True, # Usa Google Fonts CDN
	"related_modal_active": True, # Pop-up de relacionamentos ativo
	"show_ui_builder": False,      # Desativa construtor visual (produção)
	"search_model": "auth.User",   # Busca rápida no modelo User
	"changeform_format": "horizontal_tabs", # Abas horizontais para formulários
	"language_chooser": True,
	"theme": "cosmo", # Tema leve e profissional
    

	# === Customização visual ===
	"custom_css": "css/admin_custom.css", 
	"custom_js": None, 

	# === Menu superior ===
	"topmenu_links": [
		{"name": "Início", "url": "admin:index", "permissions": ["auth.view_user"]},
		{"app": "lab"},
	],

	# === Ícones personalizados ===
	"icons": {
		# Apps do sistema
		"lab": "fas fa-vials", 
		# Modelos auxiliares
		"lab.Genero": "fas fa-venus-mars",
		"lab.EstadoCivil": "fas fa-heart",
		"lab.Pais": "fas fa-flag",
		"lab.Provincia": "fas fa-map-marked-alt",
		"lab.Cidade": "fas fa-city",
		"lab.TipoAmostra": "fas fa-prescription-bottle-alt",
		"lab.UnidadeMedida": "fas fa-ruler",
		"lab.Frequencia": "fas fa-clock",
		"lab.CategoriaExame": "fas fa-layer-group",
        "lab.Metodo": "fas fa-cogs",
		"lab.Designacao": "fas fa-tags",

		# Modelos principais
		"lab.Paciente": "fas fa-user-injured", 
		"lab.Medico": "fas fa-user-md", 
		"lab.Laboratorista": "fas fa-user-nurse",
		"lab.Amostra": "fas fa-flask",
		"lab.TipoExame": "fas fa-file-medical",
		"lab.Exame": "fas fa-vials", 
		"lab.ExameMetodo": "fas fa-tools",
		"lab.Requisicao": "fas fa-file-prescription",
		"lab.RequisicaoAnalise": "fas fa-clipboard-list",
		"lab.ItemRequisicao": "fas fa-list-ul",
		"lab.Resultado": "fas fa-microscope",
		"lab.ExameCampoResultado": "fas fa-cog",
		"lab.ResultadoItem": "fas fa-notes-medical",

		# Autenticação
		"auth": "fas fa-users-cog", 
		"auth.User": "fas fa-user-shield",
		"auth.Group": "fas fa-users-cog",
	},

	# === Ícones padrão ===
	"default_icon_parents": "fas fa-folder-open",
	"default_icon_children": "fas fa-file-medical",
}

# ============================================================
# 💎 ESTILO E UX — Jazzmin UI Tweaks (AnaLinkLab)
# ============================================================

JAZZMIN_UI_TWEAKS = {
	# === Paleta de cores e layout ===
	"theme": "cosmo",  # Mantém visual leve e profissional
	"light_mode_theme": "cosmo",
    "show_jazzmin_version": False,
	"navbar": "navbar-white navbar-light",
	"navbar_fixed": True,
	"sidebar_fixed": True,
	"sidebar": "sidebar-dark-primary",
	"brand_color": "navbar-primary",
	"accent": "accent-primary",
	"layout_boxed": False,
	"layout_fluid": True,
	"layout_topnav": False,
	"layout_fixed_sidebar": True,
	"layout_fixed_navbar": True,
	"layout_fixed_footer": False,
	"layout_collapsed_sidebar": False,
    "layout_compact_sidebar": True,
	"layout_small_text_sidebar": False,
	"layout_small_text_body": False,
	"layout_small_text_footer": False,
	"layout_small_text_brand": False,
	


	"light_mode_theme_auto": False,
	"light_mode_theme": "cosmo",

	# === Botões e inputs ===
	"button_classes": {
		"primary": "btn btn-primary",
		"secondary": "btn btn-secondary",
		"info": "btn btn-info",
		"warning": "btn btn-warning",
		"danger": "btn btn-danger",
		"success": "btn btn-success",
	},

	# === Elementos de navegação ===
	"actions_sticky_top": True,         # Mantém botões de ação visíveis
	"show_ui_builder": False,           # Desativa construtor visual (produção)
	"sidebar_nav_compact_style": True,  # Menu lateral mais compacto
	"sidebar_nav_child_indent": True,   # Indenta submenus
	"sidebar_nav_flat_style": False,    # Mantém hierarquia clara
	"related_modal_active": True,       # Pop-up de relacionamentos ativo

	# === Branding refinado ===
	"body_small_text": False,
	"footer_small_text": False,
	"brand_small_text": False,
	"sidebar_small_text": False,
	"no_navbar_border": True,
    "show_jazzmin_version": False,
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

# ------------------------
# SESSÕES
# ------------------------

# 1️⃣  Termina a sessão ao fechar o navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# 2️⃣  Expira após 30 minutos (1800 segundos) de inatividade
SESSION_COOKIE_AGE = 30 * 60  # 30 minutos

# 3️⃣  Renova o tempo de vida da sessão a cada requisição ativa
SESSION_SAVE_EVERY_REQUEST = True

# 4️⃣  Se quiser reforçar limpeza de sessão (boa prática)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 5️⃣  Opcional: garantir cookies de sessão mais seguros
SESSION_COOKIE_SECURE = True          # só HTTPS
SESSION_COOKIE_HTTPONLY = True        # não acessível via JS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Lax'      # proteção CSRF básica
# ------------------------

# ============================================================
# 🎨 ADMIN PERSONALIZAÇÃO — AnaLinkLab
# ============================================================
JAZZMIN_SETTINGS = {
	# === Identidade visual ===
	"site_title": "AnaLinkLab | Painel Administrativo",
	"site_header": "AnaLinkLab Admin",
	"site_brand": "AnaLinkLab",
	"welcome_sign": "Bem-vindo ao AnaLinkLab",
	"site_logo": "img/ana_link_lab_logo.png",
	"login_logo": "img/ana_link_lab_logo.png",
   "custom_css": "css/admin_custom.css",
   "custom_js": "js/admin_custom.js",
   "show_ui_builder": False,

   "custom_template": "admin/custom_template.html",
   "custom_js": "js/admin_custom.js",
   "custom_css": "css/admin_custom.css",
   "custom_footer": "admin/custom_footer.html",

   "custom_js": "js/admin_custom.js",
   "custom_css": "css/admin_custom.css",
   "custom_footer": "admin/custom_footer.html",

   "custom_js": "js/admin_custom.js",

	"custom_css": "css/admin_custom.css",
	"custom_js": None,
   "custom_footer": None,
   "custom_template": None,

	# === Layout e UX ===
	"layout_fixed": True,
	"layout_boxed": False,
	"layout_full_width": True,
	"sidebar_collapsed": False,
	"sidebar_sticky": True,
	"navbar_sticky": True,
	"footer_fixed": False,
	"custom_scrollbar": True,
	"show_ui_builder": False,      # Desativa construtor visual (produção)
	"search_model": "auth.User",   # Busca rápida no modelo User
	"changeform_format": "horizontal_tabs", # Abas horizontais para formulários
	"language_chooser": True,
	# === Ícones personalizados ===
    "custom_icon": "img/custom_icon.png",
    

}

SESSION_COOKIE_NAME = "analinklab_session"
