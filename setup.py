#!/usr/bin/env python
# --------------------------------------------------
# Copyright The IETF Trust 2011, All Rights Reserved
# --------------------------------------------------

import re

from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()

# Get the requirements from the local requirements.txt file
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as file:
    requirements = file.read().splitlines()

# Get the requirements from the local requirements.txt file
with open(path.join(here, 'MANIFEST.in'), encoding='utf-8') as file:
    extra_files = [ l.split()[1] for l in file.read().splitlines() if l ]

def parse(changelog):
    ver_line = "^([a-z0-9+-]+) \(([^)]+)\)(.*?) *$"
    sig_line = "^ -- ([^<]+) <([^>]+)>  (.*?) *$"
    #
    entries = []
    if type(changelog) == type(''):
        changelog = open(changelog)
    for line in changelog:
        if re.match(ver_line, line):
            package, version, rest = re.match(ver_line, line).groups()
            entry = {}
            entry["package"] = package
            entry["version"] = version
            entry["logentry"] = ""
        elif re.match(sig_line, line):
            author, email, date = re.match(sig_line, line).groups()
            entry["author"] = author
            entry["email"] = email
            entry["datetime"] = date
            entry["date"] = " ".join(date.split()[:3])
            entries += [ entry ]
        else:
            entry["logentry"] += line
    changelog.close()
    entry["logentry"] = entry["logentry"].strip()
    return entries

changelog_entry_template = """
Version %(version)s (%(date)s)
------------------------------------------------

%(logentry)s"""

long_description += """
Changelog
=========
""" + "\n".join([ changelog_entry_template % entry for entry in parse("changelog")[:2] ])



import mailreplay

setup(
    name='mailreplay',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=mailreplay.__version__,

    description="Resend captured emails to localhost using SMTP",
    long_description=long_description,

    # The project's main homepage.
    #url='https://example.org/'

    # Author details
    author='Henrik Levkowetz',
    author_email='henrik@levkowetz.com',

    # Choose your license
    license='Simplified BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Mail Transport Agents',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
        #'Programming Language :: Python :: 3.4',
        #'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='SMTP email replay',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #py_modules=["debug"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['twine',],
        #'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
#    package_data={
#        'mailreplay': ['data/*', 'mailreplay.1.gz', 'debug.py', 'utils.py', 'run.py' ],
#    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('/usr/local/share/man/man1', ['mailreplay/mailreplay.1.gz',])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'mailreplay=mailreplay.run:run',
        ],
    },

    # We're reading schema files from a package directory.
    zip_safe = True,
)
