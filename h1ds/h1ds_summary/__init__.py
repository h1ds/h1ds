"""Summary database for scalar H1DS data."""

from django.conf import settings
from django.db import connections

# Name to be used for this module in H1DS header, footer links, etc.
MODULE_DOC_NAME = "Summary"

if hasattr(settings, "H1DS_SUMMARY_ROOT_URL"):
    MODULE_ROOT_URL = settings.H1DS_SUMMARY_ROOT_URL
else:
    MODULE_ROOT_URL = "summary"

TABLE_NAME_TEMPLATE = "summary_{}"


def get_summary_cursor():
    return connections['summarydb'].cursor()
