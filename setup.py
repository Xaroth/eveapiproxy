NAME            = "eveapiproxy"
MODULE_NAME     = "eveapiproxy"
VERBOSE_NAME    = "EVE API Proxy Module"

DESC = """
Very light-weight flask module to cache EVE API calls.

Should mimic EVE's api as much as possible
"""

AUTHOR_NAME     = "Steven 'Xaroth' Noorbergen"
AUTHOR_EMAIL    = "devnull@xaroth.nl"
AUTHOR_URL      = "www.xaroth.nl"
LICENSE         = 'Proprietary'

CLASSIFIERS = """
    Development Status :: 4 - Beta
    License :: Other/Proprietary License
    Operating System :: OS Independent
    Operating System :: POSIX
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Systems Administration
    Topic :: Utilities
"""

PACKAGES_EXCLUDE = ['tests', 'tests.*', 'docs', 'docs.*']

CONSOLE_SCRIPTS = []

EXTRA = {}

##############################################################################
#
# No need to edit below this line.
#  Mostly contains code to conver the data above (or from files) to
#  a format that Setuptools understands.
#
##############################################################################

from setuptools import setup, find_packages
from glob import glob
import sys
import os

SILENT = 'install' not in sys.argv
if os.environ.get('SETUP_NORUN'):
    setup = lambda *args, **kwargs: None  # noqa
    SILENT = True

CLASSIFIERS = [s.strip() for s in CLASSIFIERS.split('\n') if s]

PY3 = sys.version_info[0] == 3
JYTHON = sys.platform.startswith('java')
PYPY = hasattr(sys, 'pypy_version_info')
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DESC = DESC.strip()


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs():
    try:
        return [
            r for r in (
                strip_comments(l) for l in open(
                    os.path.join(CURRENT_DIR, 'requirements.txt')).readlines()
            ) if r]
    except:
        return []


VERSION_FILE = os.path.join(CURRENT_DIR, 'VERSION')
VERSION_OUT = os.path.join(CURRENT_DIR, MODULE_NAME, 'version_info.py')
VERSION_FORMAT = """#!/usr/bin/env python
__version__ = "%(version)s"

if __name__ == "__main__":
    print "%(name)s version %%s" %% (__version__)
"""
try:
    with open(VERSION_FILE, 'r') as fh:
        VERSION = fh.read().strip()
except:
    VERSION = '0.0.0'

with open(VERSION_OUT, 'w') as fh:
    fh.write(VERSION_FORMAT % {'name': VERBOSE_NAME, 'version': VERSION})


install_requires = reqs()

entrypoints = {}

console_scripts = entrypoints['console_scripts'] = CONSOLE_SCRIPTS

if not SILENT:
    print ""
    print "#" * 70
    print "# Installing: %s (%s)" % (NAME, VERSION)
    print "#    License: %s" % LICENSE
    print "#     Author: %s (%s)" % (AUTHOR_NAME, AUTHOR_EMAIL)
    print "#" * 70
    print "#"
    for line in DESC.splitlines():
        print "# %s" % line
    print "#"
    print "#" * 70

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    url=AUTHOR_URL,
    classifiers=CLASSIFIERS,
    platforms=['any'],
    license=LICENSE,
    packages=find_packages(exclude=PACKAGES_EXCLUDE),
    include_package_data=True,
    data_files=[],
    scripts=glob('bin/*'),
    zip_safe=False,
    install_requires=install_requires,
    entry_points=entrypoints,
    long_description=DESC,
    extras_require={},
    **EXTRA)
