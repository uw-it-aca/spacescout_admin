import json

def csv_to_json(data): 
    requests = []
    for current in data:
        #create a dictionary of the data that later gets json'ed 
        #the non_extended array is a list of the items the server specifically asks for. 
        non_extended = ["id", "name", "type", "longitude", "latitude", "height_from_sea_level", "building_name", "floor", "room_number", "description", "capacity", "display_access_restrictions", "available_hours", "manager", "organization"]
        spot_data = {}
        extended = {} 
        hours = {}
        for entry in current:
            current[entry] = current[entry].replace("\"", "")
            if entry in non_extended:
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
            #currently skips images entirely
            elif entry != "images":
                if entry == "noise_level":
                    if current[entry] == "":
                        extended[entry] = "variable"
                else:
                    extended[entry] = current[entry]
        #Combine all the dictionaries and sub-dictionaries into one
        spot_data['extended_info'] = extended
        spot_data['available_hours'] = hours
        requests.append(json.dumps(spot_data))
    return requests
