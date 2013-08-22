"""
Current h1ds version constant plus version pretty-print method.

Code copied from Fabric:
   https://github.com/bitprophet/fabric/raw/master/fabric/version.py

This functionality is contained in its own module to prevent circular import
problems with ``__init__.py`` (which is loaded by setup.py during installation,
which in turn needs access to this version information.)
"""

from subprocess import Popen, PIPE
from os.path import abspath, dirname


def git_sha():
    loc = abspath(dirname(__file__))
    p = Popen(
        "cd \"%s\" && git log -1 --format=format:%%h\ /\ %%cD" % loc,
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    )
    return p.communicate()[0]


VERSION = (1, 0, 0, 'alpha', 0)

def get_module_urls():
    return ("https://github.com/h1ds/h1ds"
            "https://github.com/h1ds/h1ds/issues/new",)

def get_version(form='short'):
    """
    Return a version string for this package, based on `VERSION`.

    Takes a single argument, ``form``, which should be one of the following
    strings:

    * ``branch``: just the major + minor, e.g. "0.9", "1.0".
    * ``short`` (default): compact, e.g. "0.9rc1", "0.9.0". For package
      filenames or SCM tag identifiers.
    * ``normal``: human readable, e.g. "0.9", "0.9.1", "0.9 beta 1". For e.g.
      documentation site headers.
    * ``verbose``: like ``normal`` but fully explicit, e.g. "0.9 final". For
      tag commit messages, or anywhere that it's important to remove ambiguity
      between a branch and the first final release within that branch.
    """
    # Setup
    versions = {}
    branch = "%s.%s" % (VERSION[0], VERSION[1])
    tertiary = VERSION[2]
    type_ = VERSION[3]
    final = (type_ == "final")
    type_num = VERSION[4]
    firsts = "".join([x[0] for x in type_.split()])
    sha = git_sha()
    sha1 = (" / %s" % sha) if sha else ""

    # Branch
    versions['branch'] = branch

    # Short
    version = branch
    if (tertiary or final):
        version += "." + str(tertiary)
    if not final:
        version += firsts
        if type_num:
            version += str(type_num)
        else:
            version += sha1
    versions['short'] = version

    # Normal
    version = branch
    if tertiary:
        version += "." + str(tertiary)
    if not final:
        if type_num:
            version += " " + type_ + " " + str(type_num)
        else:
            version += " pre-" + type_ + sha1
    versions['normal'] = version

    # Verbose
    version = branch
    if tertiary:
        version += "." + str(tertiary)
    if not final:
        if type_num:
            version += " " + type_ + " " + str(type_num)
        else:
            version += " pre-" + type_ + sha1
    else:
        version += " final"
    versions['verbose'] = version

    try:
        return versions[form]
    except KeyError:
        raise TypeError, '"%s" is not a valid form specifier.' % form

__version__ = get_version('short')
