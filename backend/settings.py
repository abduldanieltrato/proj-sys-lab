from pathlib import Path
import os

# ============================================================
# BASE & DIRETÓRIOS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "lab/static"
MEDIA_DIR = BASE_DIR / "mediafiles"
LOGS_DIR = BASE_DIR / "logs"

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

	# Terceiros
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
	{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
	{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
	{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
	{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
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
# CONFIGURAÇÕES DE TERCEIROS
# ============================================================
PHONENUMBER_DEFAULT_REGION = "MZ"

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
# SEGURANÇA
# ============================================================
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 10  # 10 minutos

# ============================================================
# AUTENTICAÇÃO
# ============================================================
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

# ============================================================
# E-MAIL
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'halteres@gmail.com'
EMAIL_HOST_PASSWORD = 'CrfGCLw@$65%20#5'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ============================================================
# CACHE
# ============================================================
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': 'unique-snowflake',
	}
}

# ============================================================
# LOGGING
# ============================================================
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {'format': '[{asctime}] {levelname} {name} — {message}', 'style': '{'},
	},
	'handlers': {
		'file': {
			'level': 'INFO',
			'class': 'logging.FileHandler',
			'filename': LOGS_DIR / 'django.log',
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'django': {'handlers': ['file'], 'level': 'INFO', 'propagate': True},
	},
}

# ============================================================
# ADMIN PERSONALIZAÇÃO
# ============================================================
ADMIN_SITE_HEADER = "Painel Administrativo"
ADMIN_SITE_TITLE = "Administração do Sistema"
ADMIN_INDEX_TITLE = "Gestão Interna de Pacientes e Resultados"
ADMIN_LOGO = os.path.join(STATIC_URL, "img/logo.png")

# ============================================================
# DJANGO DEFAULTS
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# TEMPLATES
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

# ============================================================
# LOG DIR AUTO-CREATE
# ============================================================
LOGS_DIR.mkdir(exist_ok=True)
(LOGS_DIR / 'django.log').touch(exist_ok=True)
