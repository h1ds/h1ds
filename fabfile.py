"""Fabric scripts.

Require mkvirtualenv to  be installed on all machines and  to be run in,
and WORKON_HOME defined in .bash_profile.

This is configured for Ubuntu systems.

"""
from __future__ import with_statement
import os, platform

from fabric.api import *

env.project = "h1ds"
env.git_url = "git://code.h1svr.anu.edu.au/h1ds/h1ds.git"
env.moin_dl_url = "http://static.moinmo.in/files/moin-1.9.3.tar.gz"
## TODO: use introspection to get python dir for venv.


def dev():
    """localhost with django dev server"""
    env.environment = 'development'
    if platform.linux_distribution()[0] == 'Ubuntu':
        env.mkvirtualenv = "mkvirtualenv --distribute --no-site-packages"
    else:
        # assume Arch linux
        env.mkvirtualenv = "mkvirtualenv --distribute --no-site-packages -p python2"
    env.hosts = ['localhost']
    env.server_user = os.getuid()
    env.server_group = os.getgid()

def staging():
    """localhost with apache"""
    env.environment = 'staging'
    env.hosts = ['localhost']
    if platform.linux_distribution()[0] == 'Ubuntu':
        env.mkvirtualenv = "mkvirtualenv --distribute --no-site-packages"
        env.server_user = 'www-data'
        env.server_group = 'www-data'

    else:
        # assume Arch linux
        env.mkvirtualenv = "mkvirtualenv --distribute --no-site-packages -p python2"
        env.server_user = 'http'
        env.server_group = 'http'

def production():
    """h1svr with apache."""
    env.environment = 'production'
    if platform.linux_distribution()[0] == 'Ubuntu':
        env.mkvirtualenv = "mkvirtualenv --distribute --no-site-packages"
    else:
        # assume Arch linux
        env.mkvirtualenv = "mkvirtualenv --distribute --no-site-packages -p python2"
    env.user = "datasys"
    env.hosts = ['h1svr']
    env.server_user = 'www-data'
    env.server_group = 'www-data'

def initiate():
    """To be run once only. Non-idempotent."""

    env.venv = "%(project)s_%(environment)s" %env    
    run('%(mkvirtualenv)s %(venv)s' % env)

    with prefix('workon %(venv)s && cdvirtualenv' %env):
        ## Grab the dir so we can use sudo without workon
        env_dir = run('echo $PWD')
        run('git clone %(git_url)s %(project)s' % env)
        run('mkdir -p wiki/data/plugin/theme wiki/data/pages static log db')
        run('touch wiki/data/plugin/__init__.py')
        run('touch wiki/data/plugin/theme/__init__.py')
        run('pip install fabric')
    with cd(env_dir):
        sudo('chmod -R ugo+rwX db')
        
def update():
    """Can be run multiple times. Idempotent."""

    env.settings = '%(project)s.settings_%(environment)s' % env
    env.venv = "%(project)s_%(environment)s" %env    
    
    with prefix('workon %(venv)s && cdvirtualenv' %env):
        env_dir = run('echo $PWD')
        with prefix('cd %(project)s' %env):
            run("git pull")
        
    with cd(env_dir):
        sudo('cp -r %(project)s/moin/underlay wiki' %env)
        sudo('cp %(project)s/conf/h1ds.py wiki/data/plugin/theme' %env)
        sudo('chown -R %(server_user)s:%(server_group)s wiki' %env)
        sudo('chmod -R ug+rwX wiki')
        sudo('chmod -R o-rwX wiki')

    with prefix('workon %(venv)s && cdvirtualenv' %env):
        with prefix('cd %(project)s' %env):
            if env.environment == 'development':
                run("./bootstrap.py -d")
            else:
                # TODO: remove the -d flag once git:// access is restored on code.h1svr
                run("./bootstrap.py")
            # need server perms to run db through apache, so use sudo to modify db and 
            # make sure we chown the db after to be sure.
            sudo('chown -R %s:%s ../db' %(os.getuid(), os.getgid()))
            run('./manage.py syncdb --settings=%(settings)s' % env)
            run('./manage.py collectstatic --noinput --settings=%(settings)s' % env)
            run("./manage.py migrate h1ds_core --settings=%(settings)s" % env)
            run("./manage.py migrate h1ds_mdsplus --settings=%(settings)s" % env)
            run("./manage.py migrate h1ds_summary --settings=%(settings)s" % env)
            # run("./manage.py migrate h1ds_configdb --settings=%(settings)s" % env)
            sudo('chown -R %(server_user)s:%(server_group)s ../db' %env)
            
    # TODO: shouldn't need to treat environs differently here....
    if env.environment == 'development':
        with prefix('workon %(venv)s && cdvirtualenv && cd %(project)s' %env):
            run("./manage.py loaddata data/mds_testing.json --settings=%(settings)s" % env)
            run("./manage.py loaddata data/summarydb.json --settings=%(settings)s" % env)

    elif env.environment == 'staging':
        # Create Apache config from template
        conf_template = open('%s/h1ds/conf/apache/h1ds_staging.conf.template' %env_dir)
        conf_text = conf_template.read()
        conf_template.close()
        conf_text = conf_text.replace("__venv_dir__", env_dir)
        conf_text = "# DO NOT EDIT THIS FILE DIRECTLY, MAKE CHANGES TO THE TEMPLATE FILE AND RUN fab staging deploy\n"+conf_text
        conf_file = open('%s/h1ds/conf/apache/h1ds_staging.conf' %env_dir, 'w')
        conf_file.write(conf_text)
        conf_file.close()
        ## ubuntu settings...
        # check if we already have a symlink to apache conf
        h1ds_apache_conf = '/etc/apache2/sites-available/h1ds'
        if not os.path.exists(h1ds_apache_conf):
            sudo("ln -s %s/h1ds/conf/apache/h1ds_staging.conf %s" %(env_dir, h1ds_apache_conf))
            sudo("a2ensite h1ds")
        sudo('/etc/init.d/apache2 reload')
        # arch settings...
        # check if we already have a symlink to apache conf
        #h1ds_apache_conf = '/etc/httpd/conf/vhosts/h1ds'
        # TODO - you need to manually add Include line to http.conf
        #if not os.path.exists(h1ds_apache_conf):
        #    sudo("ln -s %s/h1ds/conf/apache/h1ds_staging.conf %s" %(env_dir, h1ds_apache_conf))
        #sudo('/etc/rc.d/httpd reload')

    else:
        sudo('/etc/init.d/apache2 reload')
