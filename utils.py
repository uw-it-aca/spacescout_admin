import json
import csv
import xlrd
import xlwt
from django.http import HttpResponse
from django.utils.encoding import smart_unicode


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
        days = ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"]
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
        days = ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"]
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
        types = smart_unicode(types)
        f.writerow([spot['id'], spot['name'].encode('utf-8'), spot['location']['room_number'], spot['location']['floor'].encode('utf-8'), spot['location']['building_name'].encode('utf-8'), spot['location']['latitude'], spot['location']['longitude'], spot['organization'].encode('utf-8'), spot['manager'].encode('utf-8')] + extended_info + [spot['location']["height_from_sea_level"], spot['capacity'], spot['display_access_restrictions'].encode('utf-8'), types, available_hours])
    return response


def file_to_json(docfile):
    if docfile.content_type == 'text/csv':
        data = csv.DictReader(docfile.file)
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
