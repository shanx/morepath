import os
from setuptools import setup, find_packages

long_description = (
    open('README.rst').read()
    + '\n' +
    open('CHANGES.txt').read())

setup(name='morepath',
      version='0.3.dev0',
      description="A micro web-framework with superpowers",
      long_description=long_description,
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      url='http://morepath.readthedocs.org',
      license="BSD",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta'
        ],
      install_requires=[
        'setuptools',
        'webob >= 1.3.1',
        'venusian >= 1.0a8',
        'reg >= 0.6'
        ],
      extras_require = dict(
        test=['pytest >= 2.0',
              'pytest-cov',
              'WebTest >= 2.0.14'],
        ),
      )
