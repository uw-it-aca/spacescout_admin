#!/usr/bin/env python

from distutils.core import setup

setup(name='SpaceScout-Admin',
      version='1.0',
      description='Admin app for SpaceScout',
      install_requires=[
                        'Django>=1.4,<1.5',
                        'django-compressor<2.0',
                        'django-verbatim',
                        'django-mobility',
                        'oauth2<=1.5.211',
                        'urllib3',
                        'poster',
                        'Pillow',
                        'simplejson>=2.1',
                        'south'],
     )
