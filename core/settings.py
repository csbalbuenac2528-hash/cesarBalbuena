"""
Django settings for core project.
ERP Django — UTEC Celaya (W01 - W18).
"""

from celery.schedules import crontab
from datetime import timedelta

from pathlib import Path
import environ
import os

# ── RUTAS BASE ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── VARIABLES DE ENTORNO ────────────────────────────────────────────────────
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='dev-key-insegura-solo-para-desarrollo')
DEBUG = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# ── APPS INSTALADAS ─────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'jazzmin',  
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',        
    'allauth',                     
    'allauth.account',             
    'allauth.socialaccount',       
    'rest_framework',
    'rest_framework.authtoken',    
    'anymail',
    'django_filters',
    'whitenoise.runserver_nostatic',
    'clientes',
    'proveedores',
    'productos',
    'ventas',
    'reportes',
    'configuracion',
    'catalogo',
]

# ── MIDDLEWARE ──────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  
]

ROOT_URLCONF = 'core.urls'

# ── TEMPLATES ───────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', 
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'catalogo.context_processors.carrito_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ── BASE DE DATOS ───────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── VALIDACIÓN DE CONTRASEÑAS ───────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── INTERNACIONALIZACIÓN ────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-mx'
TIME_ZONE     = 'America/Mexico_City'
USE_I18N      = True
USE_TZ        = True

# ── ARCHIVOS ESTÁTICOS Y MEDIA ──────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── AUTENTICACIÓN ───────────────────────────────────────────────────────────
LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/productos/'
LOGOUT_REDIRECT_URL = '/'

SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
ACCOUNT_LOGIN_METHODS          = {'username'}
ACCOUNT_EMAIL_REQUIRED         = False
ACCOUNT_EMAIL_VERIFICATION     = 'none'
ACCOUNT_LOGOUT_ON_GET          = True
ACCOUNT_SESSION_REMEMBER       = True

# ── DRF ─────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ── STRIPE (W14) ────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY      = env('STRIPE_SECRET_KEY', default='sk_test_placeholder')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='pk_test_placeholder')
STRIPE_WEBHOOK_SECRET  = env('STRIPE_WEBHOOK_SECRET', default='whsec_placeholder')

# ── JAZZMIN ─────────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title": "ERP Django Admin",
    "site_header": "ERP UTEC",
    "site_brand": "ERP Django",
    "welcome_sign": "Bienvenido al ERP de UTEC Celaya",
    "copyright": "UTEC Celaya",
    "search_model": ["auth.User", "productos.Producto", "clientes.Cliente"],
    "custom_css": "css/madrid.css",
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Ver Sitio", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
}

# ── DEFAULT AUTO FIELD ──────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── CELERY (Tareas asíncronas) ──────────────────────────────────────────────
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ── CORREO ELECTRÓNICO (W17) ──────────────────────────────────────────────
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
DEFAULT_FROM_EMAIL = env(
    'DEFAULT_FROM_EMAIL',
    default='ERP Django <noreply@erp-django.com>'
)
EMAIL_SUBJECT_PREFIX = '[ERP Django] '
ADMINS = [
    ('Admin ERP', env('ADMIN_EMAIL', default='admin@erp-django.com')),
]
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default='')
ANYMAIL = {
    'SENDGRID_API_KEY': SENDGRID_API_KEY,
    'SEND_DEFAULTS': {
        'esp_extra': {'ip_pool_name': 'transactional'},
    },
}

# ── CELERY BEAT (W18) ───────────────────────────────────────────────────────

# Hora del reporte diario (hora de México), configurable sin tocar código:
#   Render → Environment → REPORTE_DIARIO_HORA=10:00
REPORTE_DIARIO_HORA = env('REPORTE_DIARIO_HORA', default='08:00')
try:
    _rep_h, _rep_m = (int(x) for x in REPORTE_DIARIO_HORA.split(':'))
except ValueError:
    _rep_h, _rep_m = 8, 0

CELERY_BEAT_SCHEDULE = {
    # Verificar stock bajo cada hora
    'verificar-stock-bajo-cada-hora': {
        'task':     'ventas.verificar_stock_bajo',
        'schedule': timedelta(hours=1),
        'args':     (5,),   # umbral = 5 unidades
        'options':  {'queue': 'erp_django'},
    },

    # Reporte de ventas diario (default 8:00 AM hora México)
    'reporte-ventas-diario-8am': {
        'task':     'ventas.reporte_ventas_diario',
        'schedule': crontab(hour=_rep_h, minute=_rep_m),
        'options':  {'queue': 'erp_django'},
    },
}

# Necesario para que Beat use la zona horaria de Django (no UTC)
CELERY_BEAT_TIMEZONE = TIME_ZONE   # 'America/Mexico_City'