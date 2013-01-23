Installing H1DS
===============

H1DS is designed to run within `virtualenv <http://www.virtualenv.org>`_
(a  python  virtual  environment).    The  installation  process  should
therefore be quite similar between different operating systems. Do date,
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


Prerequisites
-------------

In  theory,  these  prerequisites  should   be  the  only  part  of  the
installation  process which  depends on  the operating  system. However,
H1DS has only been  tested on Linux (Ubuntu and Arch  Linux), so you may
encounter some issues on other platforms.

Ubuntu 12.10
^^^^^^^^^^^^

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

    $ sudo apt-get install git python-virtualenv python-dev openssh-server gfortran libatlas-base-dev libfreetype6-dev libpng12-dev


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

Setting up the development environment
--------------------------------------

First we'll create a scratch area  virtualenv from which we'll build our
H1DS  virtualenv. The  ``mkvirtualenv``  command will  activate the  new
virtualenv  for you,  and  prefixes  the virtualenv  name  to the  shell
prompt.  The  ``cdvirtualenv``  command  takes  you  to  the  virtualenv
directory (here it's ``$WORKON_HOME/scratch``).

.. code-block:: bash

    $ mkvirtualenv --no-site-packages scratch
    (scratch)$ cdvirtualenv


We'll be  using `Fabric <http://fabfile.org>`_  to automate much  of the
installation process, so let's install it into our virtualenv now:

.. code-block:: bash

    (scratch)$ pip install fabric

Now grab the H1DS fabric script (they call it a *fabfile*) template:

.. code-block:: bash

    (scratch)$ wget http://code.h1svr.anu.edu.au/projects/h1ds/repository/raw/fabfile.py.template -O fabfile.py

Now we  create the H1DS  development virtualenv using the  fabric script
(if this doesn't work, make sure you added the virtualenvwrapper code in
your   ``~/.profile``  or   ``~/.bash_profile``   file   and  you   have
``openssh-server`` installed):

.. code-block:: bash

    (scratch)$ fab dev initiate

Now we can move across to our H1DS development virtualenv:

.. code-block:: bash

    (scratch)$ workon h1ds_development
    (h1ds_development)$ cdvirtualenv
    (h1ds_development)$ ls
    bin db h1ds include lib log media pid serverfiles static wiki
    (h1ds_development)$ cd h1ds
    (h1ds_development)$ cp fabfile.py{.template,}
    (h1ds_development)$ cp settings_development.py{.template,}
    

Open  up  ``settings_development.py``  in   an  editor  and  change  the
``SECRET_KEY`` to something unique and unguessable.


Then, install the rest of the required software:

.. code-block:: bash

    (h1ds_development)$ fab dev update



