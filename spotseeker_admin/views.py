from spotseeker_admin.forms import UploadFileForm
from spotseeker_admin.utils import file_to_json
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_unicode
from django.contrib.auth.decorators import login_required
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import mimetools
import mimetypes
import urllib2
import urllib
import oauth2 as oauth
import urlparse
import time
import json
import csv


@login_required
def upload(request):
    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))

    notice = "Upload a spreadsheet in CSV or XLS format"
    successcount = 0
    success_names = []
    failurecount = 0
    failure_desc = []
    warningcount = 0
    warning_desc = []
    failures = ''
    successes = ''
    warnings = ''
    displaysf = False
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            docfile = request.FILES['file']
            notice = ""
            try:
                data = file_to_json(docfile)
                for datum in data:
                    spot_id = datum["id"]
                    datum = datum["data"]
                    info = json.loads(datum)
                    consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
                    try:
                        images = json.loads(datum)['images']
                    except:
                        images = []

                    client = oauth.Client(consumer)
                    url = "%s/api/v1/spot" % settings.SS_WEB_SERVER_HOST

                    spot_headers = {"XOAUTH_USER": "%s" % request.user, "Content-Type": "application/json", "Accept": "application/json"}
                    spot_url = url
                    method = 'POST'
                    #use PUT when spot id is prodived to update the spot
                    if spot_id:
                        spot_url = "%s/%s" % (url, spot_id)
                        method = 'PUT'

                        #get the existing spot for its etag
                        resp, content = client.request(spot_url, 'GET')
                        if resp['status'] != '200':
                            failurecount += 1
                            if 'name' in info.keys():
                                name = info['name']
                            else:
                                name = 'NO NAME'
                            hold = {
                                'fname': name,
                                'flocation': 'id',
                                'freason': 'id not found, spot does not exist',
                            }
                            failure_desc.append(hold)
                            break
                        etag = resp['etag']
                        spot_headers['If-Match'] = etag
                    resp, content = client.request(spot_url, method, datum, headers=spot_headers)

                    #Responses 200 and 201 mean you done good.
                    if resp['status'] != '200' and resp['status'] != '201':
                        if 'name' in info.keys():
                            name = info['name']
                        else:
                            name = 'NO NAME'

                        try:
                            error = json.loads(content)
                            flocation = error.keys()[0]
                            freason = error[flocation]
                        except ValueError:
                            flocation = resp['status']
                            freason = content

                        #Add spot attempt to the list of failures
                        failurecount += 1
                        hold = {
                            'fname': name,
                            'flocation': flocation,
                            'freason': freason,
                        }
                        failure_desc.append(hold)
                    else:
                        success_names.append(" %s," % (info['name']))
                        successcount += 1

                        #jury rigging the oauth_signature
                        consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
                        client = oauth.Client(consumer)
                        resp, content = client.request(url, 'GET')
                        i = resp['content-location'].find('oauth_signature=')
                        i += len('oauth_signature=')
                        signature = resp['content-location'][i:]

                        url1 = url + '/image'
                        #there is no language for if the url doesn't work
                        for image in images:
                            try:
                                img = urllib2.urlopen(image)
                                f = open('image.jpg', 'w')
                                f.write(img.read())
                                f.close()
                                f = open('image.jpg', 'rb')

                                body = {"description": "yay", "oauth_signature": signature, "oauth_signature_method": "HMAC-SHA1", "oauth_timestamp": int(time.time()), "oauth_nonce": oauth.generate_nonce, "oauth_consumer_key": settings.SS_WEB_OAUTH_KEY, "image": f}
                                #poster code
                                register_openers()
                                datagen, headers = multipart_encode(body)
                                headers["XOAUTH_USER"] = "%s" % request.user
                                req = urllib2.Request(url1, datagen, headers)
                                response = urllib2.urlopen(req)
                            except:
                                warningcount += 1
                                if info["name"]:
                                    name = info["name"]
                                else:
                                    name = "NO NAME"
                                hold = {
                                    'fname': name,
                                    'flocation': image,
                                    'freason': "invalid image",
                                }
                                warning_desc.append(hold)
                        #might need to use https://gist.github.com/1558113 instead for the oauth request
                        #content_type = 'multipart/form-data;' #boundary=%s' % BOUNDARY
                        #oauthrequest-i have it commented for mine since i was testing poster
                        #resp, content = client.request(url, "POST", body=, headers)
                failures = "%d failed POSTs:" % (failurecount)
                warnings = "%d warnings:" % (warningcount)
                successes = "%d successful POSTs:" % (successcount)
                displaysf = True
            except TypeError:
                notice = "invalid file type %s. Please upload csv or xls spreadsheet" % (docfile.content_type)
    else:
        form = UploadFileForm()

    args = {
        'displaysf': displaysf,
        'notice': notice,
        'failures': failures,
        'failure_descs': failure_desc,
        'warnings': warnings,
        'warning_descs': warning_desc,
        'successes': successes,
        'success_names': success_names,
        'form': form,
    }
    return render_to_response('upload.html', args, context_instance=RequestContext(request))


@csrf_exempt
def getidfile(request):
    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    if request.method == 'POST':
        #dictwriter maybe?
        consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
        client = oauth.Client(consumer)
        url = "%s/api/v1/spot/?center_latitude=47.653835&center_longitude=-122.307809&distance=400000" % settings.SS_WEB_SERVER_HOST
        resp, content = client.request(url, "GET", headers={"XOAUTH_USER": "mreeve", "Content-Type": "application/json", "Accept": "application/json"})
        if content:
            spots = json.loads(content)
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = "attachment; filename=spot_data.csv"
            f = csv.writer(response)
            #extended info isn't the same for all. Need to build up a dict of all extended info keys
            extended = []
            for spot in spots:
                for info in spot['extended_info']:
                    if not info in extended:
                        extended.append(info.encode('utf-8'))
            f.writerow(['id', 'name', 'room_number', 'floor', 'building_name', 'latitude', 'longitude', 'organization', 'manager'] + extended + ["height_from_sea_level", "capacity", "display_acess_restrictions", "type", 'available_hours'])
            for spot in spots:
                days = ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"]
                available_hours = ''
                types = ''
                count = 0
                extended_info = []
                for info in extended:
                    info = info.decode('utf-8')
                    try:
                        extended_info.append(spot['extended_info'][info])
                    except:
                        extended_info.append('')
                for Type in spot['type']:
                    if count == 0:
                        types += Type
                    else:
                        types += ', ' + Type
                    count = 1
                count1 = 0
                for day in days:
                    try:
                        if count1 == 0:
                            if day == "thursday" or day == "saturday" or day == "sunday":
                                available_hours += day[0] + day[1] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                            else:
                                available_hours += day[0] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                        else:
                            if day == "thursday" or day == "saturday" or day == "sunday":
                                available_hours += ', ' + day[0] + day[1] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                            else:
                                available_hours += ', ' + day[0] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                    except:
                        pass
                    count1 = 1
                available_hours = smart_unicode(available_hours)
                types = smart_unicode(available_hours)
                f.writerow([spot['id'], spot['name'], spot['location']['room_number'], spot['location']['floor'], spot['location']['building_name'], spot['location']['latitude'], spot['location']['longitude'], spot['organization'], spot['manager']] + spot['extended_info'].values() + [spot['location']["height_from_sea_level"], spot['capacity'], spot['display_access_restrictions'], types, available_hours])
            return response
    return render_to_response('getidfile.html')
