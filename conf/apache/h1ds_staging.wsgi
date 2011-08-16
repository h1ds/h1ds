import os
import sys

import site

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
n_subdir = 2
PROJECT_ROOT = THIS_DIR
for i in range(n_subdir):
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

site_packages = os.path.join(PROJECT_ROOT, 'lib/python2.7/site-packages')
site.addsitedir(os.path.abspath(site_packages))

sys.path.insert(0, PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'h1ds.settings_staging'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
