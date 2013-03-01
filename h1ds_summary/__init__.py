"""Summary database for reduced MDSplus data."""

from django.conf import settings

# Name to be used for this module in H1DS header, footer links, etc.
MODULE_DOC_NAME = "Summary"

if hasattr(settings, "H1DS_SUMMARY_ROOT_URL"):
    MODULE_ROOT_URL = settings.H1DS_SUMMARY_ROOT_URL
else:
    MODULE_ROOT_URL = "summary" 


# Name of the SQLite summary table.
SUMMARY_TABLE_NAME = "summary"

# Don't try to use data from shots below this.
#MINIMUM_SUMMARY_TABLE_SHOT = 58198
