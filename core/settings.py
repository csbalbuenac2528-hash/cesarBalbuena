"""
Django settings for core project.
ERP Django — UTEC Celaya (W01 - W15).
"""

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
                'catalogo.context_processors.carrito_info',  # <-- LÍNEA CLAVE W13
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

# ESTA LÍNEA COMENTADA ARREGLA EL ERROR DE JAZZMIN EN LOS TESTS
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
    
    # ── ESTA ES LA LÍNEA QUE PEDISTE ──
    "custom_css": "css/madrid.css",
    # ---------------------------------
    
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Ver Sitio", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
}

# ── DEFAULT AUTO FIELD ──────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'