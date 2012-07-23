import json
import csv
import xlrd

def file_to_json(docfile): 
    if docfile.content_type == 'text/csv':
        data = csv.DictReader(docfile)
    elif docfile.content_type == 'application/vnd.ms-excel':
        #convert to dict
        workbook = xlrd.open_workbook(file_contents=docfile.read())
        sheet = workbook.sheet_by_index(0)
        keys = sheet.row_values(0)
        data = []
        for row in range(1,sheet.nrows):
            items = sheet.row_values(row)
            data_row = {}
            for item in range(len(items)):
                data_row[keys[item]] = str(items[item])
            data.append(data_row)
    else:
        raise TypeError("Invalid file type %s" % (docfile.content_type()))
    requests = []
    for current in data:
        #create a dictionary of the data that later gets json'ed 
        #the non_extended array is a list of the items the server specifically asks for. 
        non_extended = ["id", "name", "type", "capacity", "display_access_restrictions", "available_hours", "manager", "organization"]
        location = ["longitude", "latitude", "height_from_sea_level", "building_name", "floor", "room_number", "description"]
        spot_data = {}
        extended = {} 
        hours = {}
        location_data = {}
        for entry in current:
            current[entry] = current[entry].replace("\"", "")
            #Don't send empty values
            if current[entry]:
                #Handle location dict
                if entry in location:
                    location_data[entry] = current[entry]
                #Handle main dict
                elif entry in non_extended:
                    if entry == 'available_hours':
                        #assumes "M: 07:30-17:030, T: 07:30-17:30, etc" format
                        days = current[entry]
                        days = days.split(",")
                        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                        if len(days) <= 7:
                            for j in range(len(days)):
                                times = days[j].split(": ")
                                times = times[len(times)-1].split("-")
                                if len(times) == 2:
                                    hours[weekdays[j]] = [times]
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
                    spot_images = current[entry].split(", ")
                    images = []
                    for image in spot_images:
                        images.append(image)
                    spot_data[entry] = images
                #Handle extended info
                else:
                    extended[entry] = current[entry]
        #Combine all the dictionaries and sub-dictionaries into one
        spot_data['extended_info'] = extended
        spot_data['available_hours'] = hours
        spot_data['location'] = location_data
        requests.append(json.dumps(spot_data))
    return requests
