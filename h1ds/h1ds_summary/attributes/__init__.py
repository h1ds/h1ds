"""
Summary attributes scripts.

The  primary method  of adding  summary  attributes is  through the  web
data filter API.  In some cases a summary  attribute may require more
extensive   logic  or   computation  than   is  available   through  the
filters. For these, a script can be created in this directory which will
be able to be loaded by a SummaryAttribute instance.

"""


class AttributeScript(object):
    def __init__(self, shot):
        self.shot = shot

    def do_script(self):
        return None
