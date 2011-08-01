from h1ds.settings import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # TODO: don't use absolute path name
        'NAME': '/home/datasys/virtualenvs/h1ds_production/db/h1ds_production.db'
            }
    }

VERBOSE=0
