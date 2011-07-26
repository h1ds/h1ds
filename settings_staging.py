from h1ds.settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # TODO: don't use absolute path name
        'NAME': '/home/dave/.virtualenvs/h1ds_staging/db/h1ds_staging.db'
            }
    }
