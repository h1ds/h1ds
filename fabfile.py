"""Fabric scripts.

Require mkvirtualenv to  be installed on all machines and  to be run in,
and WORKON_HOME defined in .bash_profile.

"""
from __future__ import with_statement
import os

from fabric.api import *

env.project = "h1ds"
env.git_url = "git@code.h1svr.anu.edu.au:h1ds/h1ds.git"

def dev():
    """localhost with django dev server"""
    env.environment = 'development'
    env.mkvirtualenv = "mkvirtualenv -p python2 --no-site-packages --distribute"
    env.hosts = ['localhost']

def staging():
    """localhost with apache"""
    env.environment = 'staging'
    env.mkvirtualenv = "mkvirtualenv -p python2 --no-site-packages --distribute"
    env.hosts = ['localhost']

def production():
    """h1svr with apache."""
    pass

def setup():
    env.venv = "%(project)s_%(environment)s" %env    
    run('%(mkvirtualenv)s %(venv)s' % env)
    with prefix('workon %(venv)s' %env):
        run('cd $VIRTUAL_ENV && git clone %(git_url)s %(project)s' % env)
        run('mkdir $VIRTUAL_ENV/src && git clone %(moin_git_url)s moinmoin' % env)
        run('mkdir $VIRTUAL_ENV/wikidata')

def setup_moin():
    env.settings = '%(project)s.settings_%(environment)s' % env
    env.venv = "%(project)s_%(environment)s" %env    
    
    with prefix('workon %(venv)s' %env):
        env.virtual_env = os.environ['VIRTUAL_ENV']
        with cd("%(virtual_env)s/src/moinmoin" %env):
            run('git pull')
            run('python setup.py install --force --install-data=%(virtual_env)s/wikidata --record=install.log' % env)
    
def deploy():
    setup_moin()
    env.settings = '%(project)s.settings_%(environment)s' % env
    env.venv = "%(project)s_%(environment)s" %env    
    
    with prefix('workon %(venv)s' %env):
        env.virtual_env = os.environ['VIRTUAL_ENV']
        with cd("%(virtual_env)s/%(project)s" %env):
            run("git pull")
            if env.environment == 'development':
                run("./bootstrap.py -d")
            else:
                # TODO: remove the -d flag once git:// access is restored on code.h1svr
                run("./bootstrap.py -d")
            run('./manage.py syncdb --settings=%(settings)s' % env)
            run('./manage.py collectstatic --settings=%(settings)s' % env)
            run("./manage.py migrate h1ds_core --settings=%(settings)s" % env)
            run("./manage.py migrate h1ds_mdsplus --settings=%(settings)s" % env)
            run("./manage.py migrate h1ds_summary --settings=%(settings)s" % env)
            if env.environment == 'development':
                run("./manage.py loaddata data/mds_testing.json --settings=%(settings)s" % env)
                run("./manage.py loaddata data/summarydb.json --settings=%(settings)s" % env)
            else:
                sudo('/etc/init.d/apache2 reload')
