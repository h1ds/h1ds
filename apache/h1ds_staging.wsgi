import os
import sys

import site

PROJECT_ROOT = '/home/dave/.virtualenvs/h1ds_staging'
site_packages = os.path.join(PROJECT_ROOT, 'lib/python2.7/site-packages')
site.addsitedir(os.path.abspath(site_packages))

sys.path.insert(0, PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'h1ds.settings_staging'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
