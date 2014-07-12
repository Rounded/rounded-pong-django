import os

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

NOSE_ARGS = [
'--with-coverage',
'--cover-package=games',
]


AUTH_USER_MODEL = 'ponguser.PongUser'

SECRET_KEY = '+w7j5zf2#li*q!hy%l@z5a3-lnaog)igmt6ec*tx&%dt92kc15'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #our apps
    'ponguser',
    'games',

    #helper apps
    'rest_framework',
    'south',
    'django_nose',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pong.urls'

WSGI_APPLICATION = 'pong.wsgi.application'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTHENTICATION_BACKENDS = (
    'pong.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/login/'

LOGOUT_URL = '/logout/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../static/'),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, '../templates/'),
)

STATIC_ROOT = os.path.join(BASE_DIR, '../static_deploy/')

REST_FRAMEWORK = {
    'PAGINATE_BY': 100,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.OAuth2Authentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
}

########              LOAD SETTINGS FROM ENV VARS              ########
#our helper function that makes it easy to get env vars or raise an error
def get_env_variable(var_name, required=True, 
                     is_int=False, is_boolean=False, default=None):
    """ Get the environment variable or return exception """
    try:
        env_var = os.environ[var_name]
        if is_int:
            try:
                return int(env_var)
            except ValueError:
                error_msg = "%s environment variable must be a number" % var_name
                raise ImproperlyConfigured(error_msg)
        elif is_boolean:
            if env_var == "TRUE":
                return True
            else:
                return False
        else:
            return env_var
    except KeyError:
        if required:
            error_msg = "Set the %s environment variable" % var_name
            raise ImproperlyConfigured(error_msg)
        else:
            return default

#DATABASES
#TODO non-default database
DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

DEBUG = get_env_variable(
    'DEBUG',
    required=False,
    is_boolean=True,
    default=True
)

TEMPLATE_DEBUG = DEBUG

if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

ADMIN_ENABLED = get_env_variable(
    'ADMIN_ENABLED',
    required=False,
    is_boolean=True,
    default=True
)

CSRF_COOKIE_SESSION = get_env_variable(
    'CSRF_COOKIE_SESSION',
    required=False,
    is_boolean=True,
    default=False
)

SESSION_COOKIE_SECURE = get_env_variable(
    'SESSION_COOKIE_SECURE',
    required=False,
    is_boolean=True,
    default=False
)

ALLOWED_HOSTS = get_env_variable(
    'ALLOWED_HOSTS',
    required=False
).split(',') if get_env_variable('ALLOWED_HOSTS', required=False) else []

STATIC_URL = get_env_variable(
    'STATIC_URL',
    required=False,
    default='/static/'
)

#DATABASE
DATABASES['default']['ENGINE'] = get_env_variable(
    'DATABASE_DEFAULT_ENGINE',
    required=False,
    default='django.db.backends.sqlite3'
)

DATABASES['default']['NAME'] = get_env_variable(
    'DATABASE_DEFAULT_NAME', 
    required=False,
    default=os.path.join(BASE_DIR, '../db.sqlite3')
)

DATABASES['default']['USER'] = get_env_variable(
    'DATABASE_DEFAULT_USER',
    required=False,
    default=''
)

DATABASES['default']['PASSWORD'] = get_env_variable(
    'DATABASE_DEFAULT_PASSWORD',
    required=False,
    default=''
)

DATABASES['default']['HOST'] = get_env_variable(
    'DATABASE_DEFAULT_HOST',
    required=False,
    default=''
)

DATABASES['default']['PORT'] = get_env_variable(
    'DATABASE_DEFAULT_PORT',
    required=False,
    is_int=True,
    default=''
)

