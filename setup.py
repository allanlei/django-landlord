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
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'Django>=1.4',
        'django-appconf==0.5',
    ],
)
