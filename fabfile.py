"""Fabric scripts.

Require mkvirtualenv to  be installed on all machines and  to be run in,
and WORKON_HOME defined in .bash_profile.

"""
from __future__ import with_statement
import os

from fabric.api import *

env.project = "h1ds"
env.git_url = "git@code.h1svr.anu.edu.au:h1ds/h1ds.git"
env.moin_git_url = "git@code.h1svr.anu.edu.au:h1ds/moinmoin-h1ds.git"
env.moin_dl_url = "http://static.moinmo.in/files/moin-1.9.3.tar.gz"
## TODO: use introspection to get python dir for venv.
env.python_dir = 'lib/python2.7'

def dev():
    """localhost with django dev server"""
    env.environment = 'development'
    env.mkvirtualenv = "mkvirtualenv -p python2 --no-site-packages --distribute"
    env.hosts = ['localhost']
    env.venv_dir = '/home/dave/.virtualenvs'
    env.server_user = 'dave'
    env.server_group = 'dave'

def staging():
    """localhost with apache"""
    env.environment = 'staging'
    env.mkvirtualenv = "mkvirtualenv -p python2 --no-site-packages --distribute"
    env.hosts = ['localhost']
    env.venv_dir = '/home/dave/.virtualenvs'
    env.server_user = 'http'
    env.server_group = 'http'

def production():
    """h1svr with apache."""
    pass

def setup_moin():
    env.settings = '%(project)s.settings_%(environment)s' % env
    env.venv = "%(project)s_%(environment)s" %env    
    
    with prefix('workon %(venv)s' %env):
        with cd("%(venv_dir)s/%(venv)s/src/moin-1.9.3" %env):
            run('python setup.py install --force --install-data=%(venv_dir)s/%(venv)s/wikidata --record=install.log' % env)
    with cd("%(venv_dir)s/%(venv)s/wikidata/share" %env):
        sudo('chown -R %(server_user)s:%(server_group)s moin' %env)
        sudo('chmod -R ug+rwX moin')
        sudo('chmod -R o-rwX moin')
    sudo("ln -s %(venv_dir)s/%(venv)s/%(project)s/conf/h1ds.py %(venv_dir)s/%(venv)s/wikidata/share/moin/data/plugin/theme/h1ds.py" %env)

def setup():
    env.venv = "%(project)s_%(environment)s" %env    
    run('%(mkvirtualenv)s %(venv)s' % env)
    with prefix('workon %(venv)s' %env):
        run('cd $VIRTUAL_ENV && git clone %(git_url)s %(project)s' % env)
        run('mkdir $VIRTUAL_ENV/src && cd $VIRTUAL_ENV/src && wget %(moin_dl_url)s -O moin.tar.gz && tar xf moin.tar.gz' % env)
        run('mkdir $VIRTUAL_ENV/wikidata')
        run('mkdir $VIRTUAL_ENV/static')
        run('mkdir $VIRTUAL_ENV/log')
        run('mkdir $VIRTUAL_ENV/db')
        run('pip install fabric')
    setup_moin()
        
def deploy():
    env.settings = '%(project)s.settings_%(environment)s' % env
    env.venv = "%(project)s_%(environment)s" %env    
    
    with prefix('workon %(venv)s' %env):
        with cd("%(venv_dir)s/%(venv)s/%(project)s" %env):
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
            #run("./manage.py migrate h1ds_configdb --settings=%(settings)s" % env)

    # TODO: shouldn't need to treat environs differently here....
    sudo('chmod -R ugo+rwX %(venv_dir)s/%(venv)s/db' %env)
    if env.environment == 'development':
        with prefix('workon %(venv)s' %env):
            with cd("%(venv_dir)s/%(venv)s/%(project)s" %env):
                run("./manage.py loaddata data/mds_testing.json --settings=%(settings)s" % env)
                run("./manage.py loaddata data/summarydb.json --settings=%(settings)s" % env)

    elif env.environment == 'staging':
        sudo('/etc/rc.d/httpd reload')
    else:
        sudo('/etc/init.d/apache2 reload')
