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
    env.hosts = ['h1svr.anu.edu.au']
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
        run('mkdir -p wiki/data/plugin/theme wiki/data/pages wiki/data/user static log db')
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
        project_dir = os.path.join(env_dir, env.project)

    # update the h1ds dir from the repository.
    with cd(project_dir):
        run("git pull")
    
    # set up / refresh wiki directories.
    with cd(env_dir):
        sudo('cp -r %(project)s/moin/underlay wiki' %env)
        sudo('cp %(project)s/conf/h1ds.py wiki/data/plugin/theme' %env)
        sudo('chown -R %(server_user)s:%(server_group)s wiki' %env)
        sudo('chmod -R ug+rwX wiki')
        sudo('chmod -R o-rwX wiki')

    # Before we make any changes to the database, we change permissions of the db
    # directory so we can run ./manage.py without sudo. Note that we shouldn't run sudo 
    # within a virtual environment (i.e. with workon) as files like $WORKON_DIR/hook.log
    # can have their permissions changed to those of the root user, which will cause problems
    # when subsequent commands are run as a normal user.

    with cd(env_dir):
        sudo('chown -R %s:%s db' %(os.getuid(), os.getgid()))

    with prefix('workon %(venv)s && cdvirtualenv' %env):
        with prefix('cd %(project)s' %env):
            if env.environment == 'development':
                run("./bootstrap.py -d")
            else:
                run("./bootstrap.py")
            # need server perms to run db through apache, so use sudo to modify db and 
            # make sure we chown the db after to be sure.
            run('./manage.py syncdb --settings=%(settings)s' % env)
            run('./manage.py collectstatic --noinput --settings=%(settings)s' % env)
            run("./manage.py migrate h1ds_core --settings=%(settings)s" % env)
            run("./manage.py migrate h1ds_mdsplus --settings=%(settings)s" % env)
            run("./manage.py migrate h1ds_summary --settings=%(settings)s" % env)
            # run("./manage.py migrate h1ds_configdb --settings=%(settings)s" % env)

    # Now that we have finished making changes to the database, change the permissions back
    # to those appropriate for the server.
    with cd(env_dir):
        sudo('chown -R %(server_user)s:%(server_group)s db' %env)


    # TODO: shouldn't need to treat environs differently here....
    if env.environment == 'development':
        with prefix('workon %(venv)s && cdvirtualenv && cd %(project)s' %env):
            run("./manage.py loaddata data/mds_testing.json --settings=%(settings)s" % env)
            run("./manage.py loaddata data/summarydb.json --settings=%(settings)s" % env)

    else:
        # Create Apache config from template
        conf_template = open('%s/h1ds/conf/apache/h1ds_%s.conf.template' %(env_dir, env.environment))
        conf_text = conf_template.read()
        conf_template.close()
        conf_text = conf_text.replace("__venv_dir__", env_dir)
        conf_text = "# DO NOT EDIT THIS FILE DIRECTLY, MAKE CHANGES TO THE TEMPLATE FILE AND RUN fab "+env.environment+" update\n"+conf_text
        conf_file = open('%s/h1ds/conf/apache/h1ds_%s.conf' %(env_dir, env.environment), 'w')
        conf_file.write(conf_text)
        conf_file.close()
        ## ubuntu settings...
        # check if we already have a symlink to apache conf
        h1ds_apache_conf = '/etc/apache2/sites-available/h1ds'
        if not os.path.exists(h1ds_apache_conf):
            sudo("ln -s %s/h1ds/conf/apache/h1ds_%s.conf %s" %(env_dir, env.environment, h1ds_apache_conf))
            sudo("a2ensite h1ds")
        sudo('/etc/init.d/apache2 reload')
