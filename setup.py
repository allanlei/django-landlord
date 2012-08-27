from distutils.core import setup
from setuptools import find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def find_packages_in(where, **kwargs):
    return [where] + ['%s.%s' % (where, package) for package in find_packages(where=where, **kwargs)]

setup(
    name = 'django-landlord',
    version = '0.2.6',
    author = 'Allan Lei',
    author_email = 'allanlei@helveticode.com',
    description = 'Multi-tenant addons for Django',
    license = 'New BSD',
    keywords = 'multitenant django landlord',
    url = 'https://github.com/allanlei/django-landlord',
    packages=find_packages_in('landlord'),
    install_requires=[
        'Django>=1.4.1',
        'django-appconf==0.5',
    ],
)
