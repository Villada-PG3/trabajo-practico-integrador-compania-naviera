from pathlib import Path
from django.templatetags.static import static
from django.urls import reverse_lazy

# --- Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Debug
SECRET_KEY = 'django-insecure-fn^pj$)^g02^)7xwk(!^)!x$n96kue#^d=+x-slw#($@a$ejk!'
DEBUG = True
ALLOWED_HOSTS = []

# --- Apps
INSTALLED_APPS = [
    "unfold",  # Debe ir antes que django.contrib.admin
    # "unfold.contrib.filters",   # opcional
    # "unfold.contrib.forms",     # opcional
    # "unfold.contrib.inlines",   # opcional
    'django_countries',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "compania_naviera",

]

# --- Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URLs / WSGI
ROOT_URLCONF = "Config.urls"
WSGI_APPLICATION = "Config.wsgi.application"

# --- Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Carpeta templates global
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Base de datos
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N / TZ
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# --- Static
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "compania_naviera" / "static"]

# --- Defaults
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Usuario personalizado
AUTH_USER_MODEL = "compania_naviera.UsuarioPersonalizado"

# --- Login/Logout redirects
LOGIN_REDIRECT_URL = "menu_user"
LOGOUT_REDIRECT_URL = "home"

# ========== UNFOLD ==========
# Construye dinámicamente el nombre del changelist del modelo de usuario personalizado
# a partir de AUTH_USER_MODEL para evitar NoReverseMatch.
_app_label, _user_model_name = AUTH_USER_MODEL.split(".")
USER_CHANGE_LIST_NAME = f"admin:{_app_label}_{_user_model_name.lower()}_changelist"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gasleones@gmail.com'
EMAIL_HOST_PASSWORD = 'qprp jtpb iuit dulr'

UNFOLD = {
    "SITE_TITLE": "Compañía Naviera – Admin",
    "SITE_HEADER": "Panel Naviera",
    "SITE_SUBHEADER": "Operación & Pagos",
    "SITE_URL": "/",
    "THEME": "dark",  # "dark" o "light"

    "LOGIN": {
        "image": lambda request: static("img/admin-login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
    },

    # CSS/JS opcional del admin (asegurate de que existan en static/)
    "STYLES": [lambda request: static("css/admin-extra.css")],
    "SCRIPTS": [lambda request: static("js/admin-extra.js")],

    # Sidebar
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Navegación",
                "separator": True,
                "items": [
                    {"title": "Dashboard", "icon": "dashboard",
                     "link": reverse_lazy("admin:index")},
                    # Usuarios -> respeta tu usuario personalizado
                    {"title": "Usuarios", "icon": "people",
                     "link": reverse_lazy(USER_CHANGE_LIST_NAME)},
                ],
            },
            {
                "title": "Operación",
                "items": [
                    # Reservas
                    {"title": "Reservas", "icon": "bookmarks",
                     "link": reverse_lazy("admin:compania_naviera_reserva_changelist")},
                    # Pagos
                    {"title": "Pagos", "icon": "credit_card",
                     "link": reverse_lazy("admin:compania_naviera_pago_changelist")},
                ],
            },
        ],
    },
}
# ========== /UNFOLD ==========
