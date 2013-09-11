"""Django settings for h1ds project. 

Any     of      these     settings     can     be      overridden     in
settings_(development|staging|production).py.
"""
# Monkey patch to work around python threading bug.
# See http://stackoverflow.com/questions/13193278/understand-python-threading-bug
import threading
threading._DummyThread._Thread__stop = lambda x: 42

import os
import djcelery

SETTINGS_DIR = os.path.abspath(os.path.dirname(__file__))
H1DS_APP_DIR = os.path.dirname(SETTINGS_DIR)
DJANGO_PROJECT_DIR = os.path.dirname(H1DS_APP_DIR)
REPOSITORY_DIR = os.path.dirname(DJANGO_PROJECT_DIR)
VENV_DIR = os.path.dirname(REPOSITORY_DIR)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or
        # 'oracle'.
        'ENGINE': 'django.db.backends.',
        # Name, or path to database file if using sqlite3.
        'NAME': '',
        # Not used with sqlite3.
        'USER': '',
        # Not used with sqlite3.
        'PASSWORD': '',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(DJANGO_PROJECT_DIR, 'serverfiles', 'django_cache'),
        }
}

# Local time  zone for  this installation.  Choices  can be  found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not all
# choices may be available on all  operating systems. On Unix systems, a
# value  of None  will cause  Django  to use  the same  timezone as  the
# operating system. If running in a Windows environment this must be set
# to the same as your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for  this installation.  All choices can  be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you  set this to False,  Django will make some  optimizations so as
# not to load the internationalization machinery.
USE_I18N = True

# If you  set this to False,  Django will not format  dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded
# files. Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/'.join([DJANGO_PROJECT_DIR, 'media'])

# URL that handles the media served  from MEDIA_ROOT. Make sure to use a
# trailing    slash.    Examples:    "http://media.lawrence.com/media/",
# "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute  path  to the  directory  static  files should  be  collected
# to. Don't put  anything in this directory yourself;  store your static
# files  in  apps'  "static/" subdirectories  and  in  STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/'.join([DJANGO_PROJECT_DIR, 'static'])


# URL        prefix       for        static       files.        Example:
# "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files  -- CSS, JavaScript and images. Make
# sure      to      use       a      trailing      slash.      Examples:
# "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder  classes that know how to find  static files in various
# locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody. Be sure to override
# this setting in settings_production.py
SECRET_KEY = 'p=5!o!*$hyfr*8ja=e1@s!n54%jofr2xhf%egs(=-97%79v8_4'

# List  of callables  that know  how  to import  templates from  various
# sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
)


ROOT_URLCONF = 'h1ds.urls'

TEMPLATE_DIRS = (
    os.path.join(DJANGO_PROJECT_DIR, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'djcelery',
    'kombu.transport.django',
    'south',
    'django_openid_auth',
    'h1ds',
    'h1ds_summary',
    'h1ds_configdb',
    'python_field',
    'rest_framework',
    #'haystack',
    #'sphinxdoc',
)

H1DS_DATA_BACKEND = "h1ds.backends.h1"
H1DS_DATA_PREFIX = r"data"

DATA_FILTER_MODULES = (
    'h1ds.filters',
    )


TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.contrib.messages.context_processors.messages",
                               "django.core.context_processors.request")

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# A sample logging configuration. The only tangible logging performed by
# this configuration  is to send  an email to  the site admins  on every
# HTTP 500 error.
# See   http://docs.djangoproject.com/en/dev/topics/logging   for   more
# details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
        'simple': {
            'format': '%(levelname)s %(message)s'
            },
        },
    'handlers': {
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(DJANGO_PROJECT_DIR, 'log', 'django.log'),
            'maxBytes': 1024*1024*50, # 50 MB
            'backupCount': 10,
            'formatter':'verbose',
            },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'default': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

djcelery.setup_loader()

# Any MDSPlus nodes to ignore (e.g. if they crash the server...)
H1DS_MDSPLUS_NODE_BLACKLIST = []

# Extra links to be displayed in the header and on the frontpage.
# Syntax: (name, url, description)
H1DS_EXTRA_SUBLINKS = (
    ("Wiki", "/wiki", "Documentation wiki"),
    ("Activity", "/wiki/RecentChanges", "Latest changes to documentation"),
)

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

OPENID_CREATE_USERS = True
LOGIN_URL = '/openid/login'
LOGIN_REDIRECT_URL = '/'

# Customise this in your settings_(development|staging|production).py
DEFAULT_TREE = "test"

# list of extra mds trees to load into environment
# each entry should be a (name, path), for example
# EXTRA_MDS_TREES = [('extratree1', 'mdsserver::'), ('anothertree', '/data/tree'),]
EXTRA_MDS_TREES = [('test', os.path.join(DJANGO_PROJECT_DIR, 'test_mds_data'))]


# celery settings
#BROKER_BACKEND = "djkombu.transport.DatabaseTransport"
BROKER_URL = "django://"

# Method for tracking shot changes.
# Options: 
# "inotify" [not implemented] - (linux only) listen for changes to shotid.sys.
# "ping" - periodically ask MDSplus for latest shot.
SHOT_TRACKER = "ping"

# number of seconds between pinging MDSplus for latest shot
SHOT_TRACKER_PING_INTERVAL = 2


#HAYSTACK_SITECONF='h1ds.search_site'
#HAYSTACK_SEARCH_ENGINE = 'whoosh'
#HAYSTACK_WHOOSH_PATH = os.path.join(THIS_DIR, 'whoosh_index')

FIXTURE_DIRS = (os.path.join(H1DS_APP_DIR, 'fixtures'),)

# Example
#WIKI_ACL_RIGHTS_BEFORE = u"BoydBlackwell:read,write,delete,revert,admin"
#WIKI_ACL_RIGHTS_DEFAULT = u"EditorGroup:read,write,delete +All:read -All:write,delete,revert,admin"

WIKI_ACL_RIGHTS_BEFORE = u""
WIKI_ACL_RIGHTS_DEFAULT = u""

# See https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-ALLOWED_HOSTS
# You should set this to the list of used servers in settings_production.py
ALLOWED_HOSTS = ['*',]

INTERNAL_IPS = ('127.0.0.1', )
