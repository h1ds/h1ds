import os
import sys

import site

PROJECT_ROOT = '/home/datasys/virtualenvs/h1ds_production'
site_packages = os.path.join(PROJECT_ROOT, 'lib/python2.6/site-packages')
site.addsitedir(os.path.abspath(site_packages))

os.environ["CELERY_LOADER"] = "django"
os.environ["MDS_PATH"] = '/usr/local/mdsplus'
os.environ["MDSPLUS_DIR"] = '/usr/local/mdsplus'


sys.path.insert(0, PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'h1ds.settings_production'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
