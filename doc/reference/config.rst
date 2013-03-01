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
used by H1DS.

Settings for h1ds_core
^^^^^^^^^^^^^^^^^^^^^^

H1DS_EXTRA_SUBLINKS
"""""""""""""""""""

Syntax: (name, url, description)

Default:  ``(("Wiki", "/wiki", "Documentation wiki"), ("Activity", "/wiki/RecentChanges", "Latest changes to documentation"),)``

Extra links to be displayed in the header and on the frontpage.



Settings for h1ds_mdsplus
^^^^^^^^^^^^^^^^^^^^^^^^^

H1DS_MDSPLUS_NODE_BLACKLIST
"""""""""""""""""""""""""""

Default: ``[]``

A list of any MDSPlus nodes to ignore (e.g. if they crash the server).



Settings for django_openid_auth
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

OPENID_CREATE_USERS
"""""""""""""""""""

Default: ``True``

LOGIN_URL
"""""""""

Default: ``'/openid/login'``


LOGIN_REDIRECT_URL = '/'

# Customise this in your settings_(development|staging|production).py
DEFAULT_MDS_TREE = "test"

# list of extra mds trees to load into environment
# each entry should be a (name, path), for example
# EXTRA_MDS_TREES = [('extratree1', 'mdsserver::'), ('anothertree', '/data/tree'),]
EXTRA_MDS_TREES = [('test', os.path.join(VENV_DIR, 'test_mds_data'))]

# celery settings
BROKER_URL = "django://"

# Method for tracking shot changes.
# Options: 
# "inotify" - (linux only) listen for changes to shotid.sys.
SHOT_TRACKER = "inotify"


FIXTURE_DIRS = (os.path.join(THIS_DIR, 'fixtures'),)

# Example
#WIKI_ACL_RIGHTS_BEFORE = u"BoydBlackwell:read,write,delete,revert,admin"
#WIKI_ACL_RIGHTS_DEFAULT = u"EditorGroup:read,write,delete +All:read -All:write,delete,revert,admin"

WIKI_ACL_RIGHTS_BEFORE = u""
WIKI_ACL_RIGHTS_DEFAULT = u""


