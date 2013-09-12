.. _H1DS-configuration:

H1DS configuration
==================

.. _config_settings:

settings_(development|staging|production).py
--------------------------------------------

The    ``settings_development.py``,     ``settings_staging.py``    and
``settings_production.py``  files  inherit  from the  standard  django
``settings.py``. You  should familiarise  yourself with  the available
Django                           settings                           at
https://docs.djangoproject.com/en/1.5/ref/settings/.

Listed  below are  module-specific configuration  options for  modules
used by H1DS. Defaults are  those values specified in ``settings.py``,
and         are         overridden        by         values         in
``settings_(development|staging|production).py``.

Settings for h1ds
^^^^^^^^^^^^^^^^^

H1DS_EXTRA_SUBLINKS
"""""""""""""""""""

Syntax: (name, url, description)

Default:  ``(("Wiki", "/wiki", "Documentation wiki"), ("Activity", "/wiki/RecentChanges", "Latest changes to documentation"),)``

Extra links to be displayed in the header and on the frontpage.


WIKI_ACL_RIGHTS_BEFORE
""""""""""""""""""""""

Default: ``u""``

Example: ``WIKI_ACL_RIGHTS_BEFORE = u"BoydBlackwell:read,write,delete,revert,admin"``

WIKI_ACL_RIGHTS_DEFAULT
"""""""""""""""""""""""

Default: ``u""``

Example: ``WIKI_ACL_RIGHTS_DEFAULT = u"EditorGroup:read,write,delete +All:read -All:write,delete,revert,admin"``


Settings for h1ds_mdsplus
^^^^^^^^^^^^^^^^^^^^^^^^^

H1DS_MDSPLUS_ROOT_URL
"""""""""""""""""""""

Default: ``"mdsplus"``

Root URL for module.


H1DS_MDSPLUS_NODE_BLACKLIST
"""""""""""""""""""""""""""

Default: ``[]``

A list of any MDSPlus nodes to ignore (e.g. if they crash the server).


EXTRA_MDS_TREES
"""""""""""""""

Default: ``[('test', os.path.join(VENV_DIR, 'test_mds_data'))]``

list of extra mds trees to load into environment each entry should be a (name, path), for example ``EXTRA_MDS_TREES = [('extratree1', 'mdsserver::'), ('anothertree', '/data/tree'),]``


DEFAULT_TREE
""""""""""""""""

Default: ``"test"``


SHOT_TRACKER
""""""""""""
Default: ``"ping"``

Method for tracking shot changes.

Options:

* "ping" - periodically ask MDSplus for the latest shot.
* "inotify" [not implemented] - (linux only) listen for changes to shotid.sys.


Settings for h1ds_summary
^^^^^^^^^^^^^^^^^^^^^^^^^

H1DS_SUMMARY_ROOT_URL
"""""""""""""""""""""

Default: ``"summary"``

Root URL for module.


Settings for h1ds_configdb
^^^^^^^^^^^^^^^^^^^^^^^^^^

H1DS_CONFIGDB_ROOT_URL
""""""""""""""""""""""

Default: ``"configurations"``

Root URL for module.



Settings for django_openid_auth
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OPENID_CREATE_USERS
"""""""""""""""""""

Default: ``True``

LOGIN_URL
"""""""""

Default: ``'/openid/login'``


LOGIN_REDIRECT_URL
""""""""""""""""""
Default: ``'/'``


Settings for djcelery
^^^^^^^^^^^^^^^^^^^^^


BROKER_URL
""""""""""
Default: ``"django://"``

