#!/usr/bin/env python
# encoding: utf-8

from os.path import abspath, dirname, join
from setuptools import setup


here = abspath(dirname(__file__))

classifiers = (
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'License :: OSI Approved :: BSD License',
    'Intended Audience :: Developers',
    'Operating System :: POSIX :: Linux',
)

kw = {
    'name'                 : 'harstats-graphite',
    'version'              : '0.1.1',

    'description'          : 'Summarize HAR files and feed them to carbon',
    'long_description'     : open(join(here, 'README.rst')).read(),

    'author'               : 'Georgi Valkov',
    'author_email'         : 'georgi.t.valkov@gmail.com',
    'license'              : 'New BSD License',
    'url'                  : 'https://github.com/gvalkov/harstats-graphite',

    'keywords'             : 'har graphite carbon',
    'classifiers'          : classifiers,

    'py_modules'           : ['harstatsgraphite'],
    'zip_safe'             : True,
}

setup(**kw)
