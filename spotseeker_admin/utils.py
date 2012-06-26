import json

def csv_to_json(data): 
    requests = []
    #loop through each csv entry, or in this case just #1
    for current in data:
        #create a dictionary of the data 
        #the non_extended array is a list of the items the server specifically asks for. 
        #there ought to be a less ugly, hard-coded way of getting this list
        non_extended = ["id", "name", "type", "longitude", "latitude", "height_from_sea_level", "building_name", "floor", "room_number", "description", "capacity", "display_access_restrictions", "available_hours", "organization", "manager"]
        location = ["longitude", "latitude", "height_from_sea_level", "building_name", "floor", "room_number", "description"]

        spot_data = {}
        extended = {} 
        location_data = {}
        hours = {}
        for entry in current:
            if entry in non_extended:
                if entry in location:
                    location_data[entry] = current[entry]
                elif entry == 'available_hours':
                    #assumes "M: 07:30-17:030, T: 07:30-17:30, etc" format
                    days = current[entry]
                    #remove (aut, wnt, spr) indicator in some entries
                    if ")" in days:
                        day_temp = days.split(")")
                        days = day_temp[len(day_temp)-1]
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
                elif entry == "capacity":
                    if current[entry] == "":
                        current[entry] = 0
                    spot_data[entry] = current[entry]
                else:
                    spot_data[entry] = current[entry]
            elif entry != "images":
                extended[entry] = current[entry]
        #Combine all the dictionaries and sub-dictionaries into one
        spot_data['extended_info'] = extended
        spot_data['location'] = location_data
        spot_data['available_hours'] = hours
        requests.append(json.dumps(spot_data))
    return requests
