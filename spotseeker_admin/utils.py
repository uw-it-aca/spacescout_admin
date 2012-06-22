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
                    days = current[entry].split(", ")
                    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                    for j in range(len(days)):
                        times = days[j].split(": ")
                        #there is a very real possibility that stuff isn't in the perfect format.
                        if len(times) == 2:
                            times = times[1].split("-")
                        else:
                            times = times[0]
                        hours[weekdays[j]] = times
                #there needs to be an elif here for handling images, or images need to be skipped (as they are now)
                else:
                    spot_data[entry] = current[entry]
            else:
                extended[entry] = current[entry]
        #Combine all the dictionaries and sub-dictionaries into one
        spot_data['extended_info'] = extended
        spot_data['location'] = location_data
        spot_data['available_hours'] = hours
        requests.append(json.dumps(spot_data))
    return requests
