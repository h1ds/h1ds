Installing H1DS
===============

H1DS is designed to run within `virtualenv <http://www.virtualenv.org>`_
(a  python  virtual  environment).    The  installation  process  should
therefore be quite similar between different operating systems. To date,
H1DS has only been used with Linux,  but with modest changes to the code
it  should  run  on  any  other operating  system  supported  by  Python
(Windows, Linux/Unix, Mac OS X).


H1DS is  known to run on  Python 2.7. It  is built using the  Django web
framework,  currently  version 1.3  which  supports  Python 2.4  to  2.7,
however  it  is unlikely  Python  2.4  or 2.5  will  work  due to  other
libraries used by H1DS.


.. note::

    There is  an open issue  in the H1DS  issue tracker to  find exactly
    which       versions       of       Python       are       supported
    (`H1DS issue #92 <http://code.h1svr.anu.edu.au/issues/92>`_)

Currently `MDSplus <http://www.mdsplus.org>`_ is the only supported data
system.  While  H1DS is designed  to be modular  such that it  will work
with data  systems other than MDSplus,  there are no immediate  plans to
support  other systems.  If  you are  interested in  using  H1DS with  a
non-MDSplus system,  I'd be  happy to  help you  with the  required code
changes.

.. _installing_h1ds_prerequisites:

Prerequisites
-------------

In  theory,  these  prerequisites  should   be  the  only  part  of  the
installation  process which  depends on  the operating  system. However,
H1DS has only been  tested on Linux (Ubuntu and Arch  Linux), so you may
encounter some issues on other platforms.

Ubuntu 12.04 LTS
^^^^^^^^^^^^^^^^

First, install  `git <http://git-scm.com/>`_, virtualenv and  the python
header files (needed for compiling  some python libraries). Currently we
also need  openssh server,  as the script  which deploys  the production
server over  ssh is also  used to set up  the development server  on the
local           computer            (`H1DS           issue           #93
<http://code.h1svr.anu.edu.au/issues/93>`_).      We    also     install
``gfortran`` and ``libatlas-base-dev`` so we  can build ``numpy`` in our
virtualenv,  and ``libfreetype6-dev``  and  ``libpng12-dev``  so we  can
build ``matplotlib`` :

.. code-block:: bash

    $ sudo apt-get install git python-virtualenv python-dev ssh gfortran build-essential libatlas-base-dev libfreetype6-dev libpng12-dev


We               also               use               `virtualenvwrapper
<http://virtualenvwrapper.readthedocs.org>`_   to   manage  the   python
virtual environments. Unfortunately, the  recent versions of Ubuntu have
`a   problem   with   the   Ubuntu  packaged   version   of   virtualenv
<https://bugs.launchpad.net/ubuntu/+source/virtualenvwrapper/+bug/870097>`_
which causes  problems for  H1DS. Instead, we  install virtualenvwrapper
via the  `pip installer <http://pip-installer.org>`_ (which  should have
been installed as a dependency of python-virtualenv):

.. code-block:: bash

    $ sudo pip install virtualenvwrapper


.. note::

    The Ubuntu virtualenv package only causes  a problem when it is used
    with  sudo, which  is required  when deploying  a production  server
    (e.g. when  we need to  restart Apache). If  you are looking  to run
    H1DS just on your  own computer you might be able  to use the Ubuntu
    package. However, to keep things simple here we'll assume virtualenv
    has been installed via pip.


Now add the following to both your ``~/.bashrc`` and ``~/.profile`` files, replacing my_username
with   your  own   username  (you   can  use   whatever  you   like  for
``$WORKON_HOME``, it will be where all your virtualenvs are stored):

.. code-block:: bash

    if [ $USER == my_username ]; then
        export WORKON_HOME=$HOME/v
        source /usr/local/bin/virtualenvwrapper.sh
    fi

Then, either start a new terminal or read in your ``.bashrc`` file:

.. code-block:: bash

    $ source ~/.bashrc

The ``~/.profile`` is read when you  run the Fabric script (which uses a
login    shell,     and    therefore    checks     ``~/.profile``    (or
``~/.bash_profile``)  rather  than  ``~/.bashrc``,  which  is  read  for
non-login shells.


If you  don't already  have MDSplus  installed, follow  the installation
instructions    for     Ubuntu    which     you    can     find    here:
`<http://www.mdsplus.org/index.php/Latest_Ubuntu_Packages>`_


Setting up the development environment
--------------------------------------

We'll first create our  python virtual environment. The ``mkvirtualenv``
command  will activate  the new  virtualenv  for you,  and prefixes  the
virtualenv name to the shell prompt.  The ``cdvirtualenv`` command takes
you      to      the      virtualenv      directory      (here      it's
``$WORKON_HOME/h1ds_development``).

.. code-block:: bash

    $ mkvirtualenv --no-site-packages h1ds_development
    (h1ds_development)$ cdvirtualenv



We'll be  using `Fabric <http://fabfile.org>`_  to automate much  of the
installation process, so let's install it into our virtualenv now:

.. code-block:: bash

    (h1ds_development)$ pip install fabric


Now grab the H1DS project from the git repository:

.. code-block:: bash

    (h1ds_development)$ git clone git://code.h1svr.anu.edu.au/h1ds/h1ds.git
    (h1ds_development)$ cd h1ds

In the H1DS project we need  to create a couple of initial configuration
files from the provided templates; the  H1DS fabric script (they call it
a *fabfile*) and the Django project settings file:

.. code-block:: bash

    (h1ds_development)$ cp fabfile.py{.template,}
    (h1ds_development)$ cp settings_development.py{.template,}

Open  up  ``settings_development.py``  in   an  editor  and  change  the
``SECRET_KEY`` to something unique and unguessable.


Then, install the rest of the required software using the fabric script:

.. code-block:: bash

    (h1ds_development)$ fab dev update

.. note:: 

    If the above doesn't work, make sure you added the virtualenvwrapper
    code in your ``~/.profile`` or ``~/.bash_profile`` file and you have
    ``ssh`` installed):

During  the update  you'll  be asked  if  you want  to  create a  Django
superuser  account. Answer  ``yes``  and provide  the requested  details
(name, email etc).


You can now start the development server via:

.. code-block:: bash

    (h1ds_development)$ ./manage.py runcserver --settings=h1ds.settings_development

You can update H1DS any time by repeating the ``fab dev update`` command.

Setting up a staging environment
--------------------------------

If you are making  changes to the H1DS code for  a production server, it
helps to have the production  environment replicated in a staging server
so  you can  make  sure  your code  changes  behave  as expected  before
changing the code on your public website.


Here we use `VirtualBox <https://www.virtualbox.org/>`_ to replicate the
production server,  run on the  development system (i.e. laptop)  with a
host-only network connection between  the development system and staging
server. We will use Ubuntu 12.04 LTS for the staging server.


First, you'll  need to install VirtualBox  and start a new  Ubuntu 12.04
guest operating system. There are plenty of resources on the web to help
you with that, so I won't go into  any detail here on how to do it. Once
you have  your Ubuntu  virtual server  working, follow  the prerequisite
steps above (see :ref:`installing_h1ds_prerequisites`).


You'll also need to install the apache webserver and wsgi module:

.. code-block:: bash

    $ sudo apt-get install apache2 libapache2-mod-wsgi

Also deactivate the default apache site on your staging server:

.. code-block:: bash

    $ sudo a2dissite 000-default
    $ sudo service apache2 reload


Next, set up a host-only network connection for your staging server. You
may need to load the ``vboxnetadp`` and ``vboxnetflt`` kernel modules on
your host (development) system. Then, in the general VirtualBox settings
(``File -> Preferences...``) go to the network settings and create a new
host-only  network. Then  in the  VirtualBox settings  for your  staging
server select  ``Network`` and add  a new adapter attached  to host-only
adapter and select the newly created  host-only network as its name (you
may need to power off the virtual machine to edit the settings).


With your staging  server powered up, type ``ip addr``  to find the IP
address of your staging server on  the host-only network, it should be
something like  ``192.168.56.101``, and will likely  be ``eth1``. Edit
the  staging  server  settings  in `fabfile.py`  in  your  development
environment::

    STAGING_USER = "username" # user on VirtualBox guest system
    STAGING_HOST = "192.168.56.101" # Host-only IP address of VirtualBox guest system


Next, in your development virtualenv, run:

.. code-block:: bash

    (h1ds_development)$ fab staging setup
    (h1ds_development)$ cp settings_staging.py{.template,}

Make any desired  changes to ``settings_staging.py`` --  you should at
least edit  ``SECRET_KEY`` to  something unique and  unguessable. Then
update the staging server:

.. code-block:: bash

    (h1ds_development)$ fab staging update


You should be able to see H1DS running in a browser at the host-only IP address of the staging server (i.e. ``http://192.168.56.101``).


