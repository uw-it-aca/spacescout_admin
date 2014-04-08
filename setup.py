#!/usr/bin/env python

from distutils.core import setup

setup(name='SpaceScout-Server',
      version='1.0',
      description='REST Backend for SpaceScout',
      install_requires=['Django==1.4.5','django-compressor','django-verbatim','django-mobility','oauth2','urllib3','poster','PIL','simplejson','south'],
     )
