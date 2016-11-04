from poster.streaminghttp import register_openers
from django.utils.encoding import smart_unicode
from poster.encode import multipart_encode
from django.http import HttpResponse
from django.conf import settings
import datetime
import oauth2 as oauth
import urllib2
import json
import time
import csv
import xlrd
import xlwt
import os
import codecs


def write_xls(spots):
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = "attachment; filename=spot_data.xls"
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('spot_data')
    extended = []
    for spot in spots:
        for info in spot['extended_info']:
            if not info in extended:
                extended.append(info.encode('utf-8'))
    header = ['id', 'name', 'room_number', 'floor', 'building_name', 'latitude', 'longitude', 'organization', 'manager'] + extended + ["height_from_sea_level", "capacity", "display_access_restrictions", "type", 'available_hours']
    collumn = 0
    for info in header:
        worksheet.write(0, collumn, info)
        collumn += 1
    row = 1
    for spot in spots:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        available_hours = ''
        types = ''
        count = 0
        extended_info = []
        for info in extended:
            info = info.decode('utf-8')
            try:
                extended_info.append(spot['extended_info'][info].encode('utf-8'))
            except:
                extended_info.append('')
        for Type in spot['type']:
            if count == 0:
                types += Type.encode('utf-8')
            else:
                types += ', ' + Type.encode('utf-8')
            count = 1
        count1 = 0
        for day in days:
            try:
                if count1 == 0:
                    if day == "thursday" or day == "sunday":
                        available_hours += day[0] + day[1] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                    else:
                        available_hours += day[0] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                else:
                    if day == "thursday" or day == "sunday":
                        available_hours += ', ' + day[0] + day[1] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                    else:
                        available_hours += ', ' + day[0] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
            except:
                pass
            count1 = 1
        available_hours = smart_unicode(available_hours)
        types = smart_unicode(types)
        data_row = [spot['id'], spot['name'].encode('utf-8'), spot['location']['room_number'], spot['location']['floor'].encode('utf-8'), spot['location']['building_name'].encode('utf-8'), spot['location']['latitude'], spot['location']['longitude'], spot['organization'].encode('utf-8'), spot['manager'].encode('utf-8')] + extended_info + [spot['location']["height_from_sea_level"], spot['capacity'], spot['display_access_restrictions'].encode('utf-8'), types, available_hours]
        collumn = 0
        for info in data_row:
            worksheet.write(row, collumn, info)
            collumn += 1
        row += 1
    workbook.save(response)
    return response


def write_csv(spots):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = "attachment; filename=spot_data.csv"
    f = csv.writer(response)
    #extended info isn't the same for all. Need to build up a dict of all extended info keys
    extended = []
    for spot in spots:
        for info in spot['extended_info']:
            if not info in extended:
                extended.append(info.encode('utf-8'))
    f.writerow(['id', 'name', 'room_number', 'floor', 'building_name', 'latitude', 'longitude', 'organization', 'manager'] + extended + ["height_from_sea_level", "capacity", "display_access_restrictions", "type", 'available_hours'])
    for spot in spots:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        available_hours = ''
        types = ''
        count = 0
        extended_info = []
        for info in extended:
            info = info.decode('utf-8')
            try:
                extended_info.append(spot['extended_info'][info].encode('utf-8'))
            except:
                extended_info.append('')
        for Type in spot['type']:
            if count == 0:
                types += Type.encode('utf-8')
            else:
                types += ', ' + Type.encode('utf-8')
            count = 1
        count1 = 0
        for day in days:
            try:
                if count1 == 0:
                    if day == "thursday" or day == "sunday":
                        available_hours += day[0] + day[1] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                    else:
                        available_hours += day[0] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                else:
                    if day == "thursday" or day == "sunday":
                        available_hours += ', ' + day[0] + day[1] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
                    else:
                        available_hours += ', ' + day[0] + ': ' + spot['available_hours'][day][0][0] + '-' + spot['available_hours'][day][0][1]
            except:
                pass
            count1 = 1
        available_hours = smart_unicode(available_hours)
        types = smart_unicode(types)
        f.writerow([spot['id'], spot['name'].encode('utf-8'), spot['location']['room_number'], spot['location']['floor'].encode('utf-8'), spot['location']['building_name'].encode('utf-8'), spot['location']['latitude'], spot['location']['longitude'], spot['organization'].encode('utf-8'), spot['manager'].encode('utf-8')] + extended_info + [spot['location']["height_from_sea_level"], spot['capacity'], spot['display_access_restrictions'].encode('utf-8'), types, available_hours])
    return response


def file_to_json(docfile):
    if docfile.content_type == 'text/csv':
        dialect = csv.Sniffer().sniff(codecs.EncodedFile(docfile, "utf-8").read())
        docfile.open()
        data = csv.DictReader(codecs.EncodedFile(docfile, "utf-8"), dialect=dialect)
    elif docfile.content_type == 'application/vnd.ms-excel' or docfile.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        #convert .xls or .xlsx to dict
        workbook = xlrd.open_workbook(file_contents=docfile.read())
        sheet = workbook.sheet_by_index(0)
        keys = sheet.row_values(0)
        data = []
        for row in range(1, sheet.nrows):
            items = sheet.row_values(row)
            data_row = {}
            for item in range(len(items)):
                try:
                    data_row[keys[item]] = items[item].encode('utf-8')
                except:
                    if items[item] == int(items[item]):
                        data_row[keys[item]] = str(int(items[item]))
                    else:
                        data_row[keys[item]] = str(items[item])
            data.append(data_row)
    else:
        raise TypeError("Invalid file type %s" % (docfile.content_type()))
    requests = []
    errors = []
    for current in data:
        #create a dictionary of the data that later gets json'ed
        #the non_extended array is a list of the items the server specifically asks for.
        non_extended = ["id", "name", "type", "capacity", "display_access_restrictions", "available_hours", "manager", "organization"]
        location = ["longitude", "latitude", "height_from_sea_level", "building_name", "floor", "room_number", "description"]
        spot_data = {}
        extended = {}
        hours = {}
        location_data = {}
        spot_id = ""
        try:
            for entry in current:
                #Remove extraneous quotes
                current[entry] = current[entry].replace("\"", "")
                #Don't send empty values
                if current[entry]:
                    current[entry] = current[entry].decode('utf-8')
                    if entry == 'id':
                        spot_id = current[entry]
                    #Handle location dict
                    elif entry in location:
                        location_data[entry] = current[entry]
                    #Handle main dict
                    elif entry in non_extended:
                        if entry == 'available_hours':
                            #assumes "M: 07:30-17:030, T: 07:30-17:30, etc" format
                            days = current[entry]
                            days = days.split(",")
                            weekdays = {"m": "monday", "t": "tuesday", "w": "wednesday", "th": "thursday", "f": "friday", "s": "saturday", "su": "sunday"}
                            for day in days:
                                times = day.split(": ")
                                day = times[0]
                                day = day.strip()
                                day = day.lower()
                                times = times[len(times) - 1].split("-")
                                if len(times) == 2:
                                    try:
                                        hours[weekdays[day]]
                                        prev = True
                                    except:
                                        prev = False
                                    try:
                                        if not prev:
                                            hours[weekdays[day]] = [times]
                                        else:
                                            hours[weekdays[day]] += [times]
                                    except:
                                        errors.append({"name": current["name"], "location": entry, "error": "unable to parse hours"})
                                        raise Warning
                                else:
                                    errors.append({"name": current["name"], "location": entry, "error": "unable to parse hours"})
                                    raise Warning
                        elif entry == "type":
                            spot_types = current[entry].split(", ")
                            types = []
                            for spot_type in spot_types:
                                types.append(spot_type)
                            spot_data[entry] = types
                        else:
                            spot_data[entry] = current[entry]
                    #Handle images
                    elif entry == "images":
                        spot_images = current[entry].split(",")
                        images = []
                        for image in spot_images:
                            if image != "":
                                image.strip()
                                images.append(image)
                        spot_data[entry] = images
                    #Handle extended info
                    else:
                        extended[entry] = current[entry]
            #Combine all the dictionaries and sub-dictionaries into one
            spot_data['extended_info'] = extended
            spot_data['available_hours'] = hours
            spot_data['location'] = location_data
            spot_request = {"id": spot_id, "data": json.dumps(spot_data)}
            requests.append(spot_request)
        except:
            pass
    return {"data": requests, "errors": errors}


# This function was copy and pasted to spacescout_labtracker utils.py
def upload_data(request, data):
    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))
    success_names = []
    failure_descs = []
    warning_descs = []
    puts = []
    posts = []
    for datum in data:
        try:
            spot_id = datum["id"]
        except:
            spot_id = None
        try:
            etag = datum["etag"]
            if not etag:
                etag = "There was an error!"
        except:
            etag = None
        datum = datum["data"]

        info = json.loads(datum)
        consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
        try:
            images = info['images']
        except:
            images = []

        if 'name' in info.keys():
            spot_name = info['name']
        else:
            spot_name = 'NO NAME'

        client = oauth.Client(consumer)
        url = "%s/api/v1/schema" % settings.SS_WEB_SERVER_HOST

        spot_headers = {"X-OAuth-User": "%s" % request.user, "Content-Type": "application/json", "Accept": "application/json"}
        spot_url = url
        method = 'POST'
        #use PUT when spot id is prodived to update the spot
        if spot_id:
            spot_url = "%s/%s" % (url, spot_id)
            method = 'PUT'
            #get the existing spot for its etag
            resp, content = client.request(spot_url, 'GET')
            if resp['status'] != '200':
                hold = {
                    'fname': spot_name,
                    'flocation': 'id',
                    'freason': 'id not found, spot does not exist',
                }
                failure_descs.append(hold)
                continue  # immediately restarts at the beginning of the loop
            if not etag:
                etag = resp['etag']
            spot_headers['If-Match'] = etag
        resp, content = client.request(spot_url, method, datum, headers=spot_headers)

        #Responses 200 and 201 mean you done good.
        if resp['status'] != '200' and resp['status'] != '201':
            try:
                error = json.loads(content)
                flocation = error.keys()[0]
                freason = error[flocation]
            except ValueError:
                flocation = resp['status']
                freason = content

            #Add spot attempt to the list of failures
            hold = {
                'fname': spot_name,
                'flocation': flocation,
                'freason': freason,
            }
            failure_descs.append(hold)
        else:
            success_names.append({'name': spot_name, 'method': method})

            if content:
                url1 = spot_url
            elif resp['location']:
                url1 = '%s/image' % resp['location']
            else:
                hold = {
                    'fname': spot_name,
                    'flocation': image,
                    'freason': "could not find spot idea; images not posted",
                }
                warning_descs.append(hold)
                break

            #jury rigging the oauth_signature
            consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
            client = oauth.Client(consumer)
            resp, content = client.request(url, 'GET')
            i = resp['content-location'].find('oauth_signature=')
            i += len('oauth_signature=')
            signature = resp['content-location'][i:]

            #there is no language for if the url doesn't work
            if method == 'POST':
                for image in images:
                    print '-' * 20
                    print image
                    try:
                        # Stopgap 404 catching, this should be added to warning_descs in a smart way eventually.
                        print "attempting to open image..."
                        try:
                            img = urllib2.urlopen(image)
                            print "img type: {0}".format(img.info().type)
                        except Exception as err:
                            if err.code:
                                print "Error code {0}".format(err.code)
                            if err.reason:
                                print "Error reason {0}".format(err.reason)

                        f = open('image.jpg', 'w')
                        f.write(img.read())
                        f.close()
                        f = open('image.jpg', 'rb')

                        body = {"description": "yay", "image": f}
                        authorization = 'OAuth oauth_version="1.0",oauth_nonce="%s",oauth_timestamp="%d",oauth_consumer_key="%s",oauth_signature_method="HMAC-SHA1",oauth_signature="%s"' % (oauth.generate_nonce(), int(time.time()), settings.SS_WEB_OAUTH_KEY, signature)

                        #poster code
                        register_openers()
                        datagen, headers = multipart_encode(body)
                        headers["X-OAuth-User"] = "%s" % request.user
                        headers["Authorization"] = authorization
                        req = urllib2.Request(url1, datagen, headers)
                        response = urllib2.urlopen(req)
                    except:
                        hold = {
                            'fname': spot_name,
                            'flocation': image,
                            'freason': "invalid image",
                        }
                        warning_descs.append(hold)
                    print '-' * 20
                    print '\n'

                # 'image.jpg' being saved in admin_proj may just be a bug that only happens in development
                # this may end up being unneccessary
                # delete that 'image.jpg' created in the directory from above code
                myfile = "image.jpg"
                if os.path.isfile(myfile):
                    os.remove(myfile)

            #might need to use https://gist.github.com/1558113 instead for the oauth request
            #content_type = 'multipart/form-data;' #boundary=%s' % BOUNDARY
            #oauthrequest-i have it commented for mine since i was testing poster
            #resp, content = client.request(url, "POST", body=, headers)
        if method == 'POST':
            posts.append(spot_name)
        elif method == 'PUT':
            puts.append(spot_name)
    return {
        'success_names': success_names,
        'failure_descs': failure_descs,
        'warning_descs': warning_descs,
        'posts': posts,
        'puts': puts,
    }


def to_datetime_object(date_string):
    """Only for when the string is in the format 'yyyy-mm-ddThh:mm:ss'
    """
    time_parts = date_string.split('.')
    time_parts[1] = time_parts[1].split('+')[0]
    result = datetime.datetime.strptime(time_parts[0], '%Y-%m-%dT%H:%M:%S')
    result = result.replace(microsecond=int(time_parts[1]))
    return result
