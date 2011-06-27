#!/usr/bin/env python
# bootstrap.py
# Bootstrap and setup a virtualenv with the specified requirements.txt
import os
import sys
import subprocess
from optparse import OptionParser


usage = """usage: %prog [options]"""
parser = OptionParser(usage=usage)
parser.add_option("-c", "--clear", dest="clear", action="store_true",
                  help="clear out existing virtualenv")
parser.add_option("-d", "--dev", dest="dev", action="store_true",
                  help="Use requirements/apps.dev.txt")


def main():
    if "VIRTUAL_ENV" not in os.environ:
        sys.stderr.write("$VIRTUAL_ENV not found.\n\n")
        parser.print_usage()
        sys.exit(-1)
    (options, pos_args) = parser.parse_args()
    virtualenv = os.environ["VIRTUAL_ENV"]
    if options.clear:
        subprocess.call(["virtualenv", "--clear", "--distribute", virtualenv])
    file_path = os.path.dirname(__file__)
    if options.dev:
        subprocess.call(["pip", "install", "-E", virtualenv, "--requirement",
                         os.path.join(file_path, "requirements/apps.dev.txt")])
    else:
        subprocess.call(["pip", "install", "-E", virtualenv, "--requirement",
                         os.path.join(file_path, "requirements/apps.txt")])


if __name__ == "__main__":
    main()
    sys.exit(0)
