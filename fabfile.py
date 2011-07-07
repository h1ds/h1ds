from __future__ import with_statement
import os

from fabric.api import *

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
env.home, env.project = os.path.split(THIS_DIR)


def dev():
    env.environment = 'development'
    env.root = env.home
    env.code_root = THIS_DIR
    env.settings = '%(project)s.settings_%(environment)s' % env

def setup():
    if env.environment == 'development':
        local("./manage.py syncdb --settings=%(settings)s" % env)
        local("./manage.py migrate h1ds_core --settings=%(settings)s" % env)
        local("./manage.py migrate h1ds_mdsplus --settings=%(settings)s" % env)
        local("./manage.py migrate h1ds_summary --settings=%(settings)s" % env)
        local("./manage.py loaddata data/mds_testing.json --settings=%(settings)s" % env)
        local("./manage.py loaddata data/summarydb.json --settings=%(settings)s" % env)
    else:
        pass
