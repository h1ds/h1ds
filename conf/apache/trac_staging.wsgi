import os

# Find absolute path of project.
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
n_subdir = 3
PROJECT_ROOT = THIS_DIR
for i in range(n_subdir):
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

VENV_ROOT = os.path.dirname(PROJECT_ROOT)
TRAC_ROOT = os.path.join(VENV_ROOT, "trac")

os.environ['TRAC_ENV'] = TRAC_ROOT
os.environ['PYTHON_EGG_CACHE'] = os.path.join(TRAC_ROOT, "eggs")

import trac.web.main
application = trac.web.main.dispatch_request