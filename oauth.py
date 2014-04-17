""" Copyright 2012, 2013 UW Information Technology, University of Washington

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from django.conf import settings
import oauth2


def oauth_initialization():
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    if not hasattr(settings, "SS_ADMIN_OAUTH_KEY") and not hasattr(settings, 'SS_WEB_OAUTH_KEY'):
        raise(Exception("Required setting missing: SS_ADMIN_OAUTH_KEY"))
    if not hasattr(settings, "SS_ADMIN_OAUTH_SECRET") and not hasattr(settings, 'SS_WEB_OAUTH_SECRET'):
        raise(Exception("Required setting missing: SS_ADMIN_OAUTH_SECRET"))

    oauth_key = ""
    if hasattr(settings, "SS_ADMIN_OAUTH_KEY"):
        oauth_key = settings.SS_ADMIN_OAUTH_KEY
    else:
        oauth_key = settings.SS_WEB_OAUTH_KEY

    oauth_secret = ""
    if hasattr(settings, "SS_ADMIN_OAUTH_SECRET"):
        oauth_secret = settings.SS_ADMIN_OAUTH_SECRET
    else:
        oauth_secret = settings.SS_WEB_OAUTH_SECRET


    consumer = oauth2.Consumer(key=oauth_key, secret=oauth_secret)
    client = oauth2.Client(consumer)

    return consumer, client

def oauth_nonce():
    return oauth2.generate_nonce()
