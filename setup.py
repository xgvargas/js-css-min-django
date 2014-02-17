#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup
import pkg_resources
import codecs
import jscssmin


with codecs.open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    install_requires = [str(req) for req in pkg_resources.parse_requirements(f)]

setup(
    name='jscssmin',
    version=jscssmin.__version__,
    license="Apache",
    description='JS and CSS automated merge and minifier',
    long_description=long_description,
    author='Gustavo vargas',
    author_email='xgvargas@gmail.com',
    url='https://github.com/xgvargas/js-css-min-django',
    #packages=find_packages(exclude=['*test*']),
    py_modules = ['jscssmin'],
    package_data={'': ['LICENSE']},
    scripts=['scripts/jscssmin'],
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Pre-processors',
        'Framework :: Django',
    ],
)
