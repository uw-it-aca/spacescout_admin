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
from django.utils.translation import ugettext as _
import urllib
import simplejson
from django.http import Http404
from django.http import HttpResponse
from spacescout_admin.oauth import oauth_initialization


def SpotSearch(request):
    # Required settings for the client
    consumer, client = oauth_initialization()

    search_args = {
#        'manager': '',
#        'editors': '',
        'limit': '0'
   }

    json = get_space_search_json(client, search_args)
    json = simplejson.loads(json)
    i18n_json = []
    for space in json:

        #
        # FILTER: REMOTE_USER in group u_spotseeker_admins || params["manager"] == REMOTE_USER
        #

        string_val = ''
        for x in range(0, len(space['type'])):
            if x is 0:
                string_val = _(space['type'][x])
            else:
                string_val = string_val + ', ' + _(space['type'][x])
        space['type'] = string_val
        i18n_json.append(space)
    json = simplejson.dumps(i18n_json)
    response = HttpResponse(json)

    response["Content-type"] = "application/json"

    return response


def SpotImage(request, spot_id, image_id):
    # Required settings for the client
    consumer, client = oauth_initialization()

    url = "{0}/api/v1/spot/{1}/image/{2}".format(settings.SS_WEB_SERVER_HOST, spot_id, image_id)

    resp, content = client.request(url, 'GET')

    if resp.status != 200:
        response = HttpResponse("Error loading image")
        response.status_code = resp.status_code
        return response

    response = HttpResponse(content)

    response["Content-type"] = "application/json"

    return response


def get_space_search_json(client, options):
    # 
    # Until we can search on manager == REMOTE_USER
    #

    args = []
    #for key in options:
    #    if isinstance(options[key], types.ListType):
    #        for item in options[key]:
    #            args.append("{0}={1}".format(urllib.quote(key), urllib.quote(item)))
    #    else:
    #        args.append("{0}={1}".format(urllib.quote(key), urllib.quote(options[key])))

    #url = "{0}/api/v1/spot/search?{1}".format(settings.SS_WEB_SERVER_HOST, "&".join(args))

    url = "{0}/api/v1/spot/all".format(settings.SS_WEB_SERVER_HOST, "&".join(args))

    resp, content = client.request(url, 'GET')

    if resp.status == 200:
        return content

    return '[]'
