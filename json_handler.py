import json

#################### Room Server ####################
def add_room(roomname):
    # add room to json file
    # if roomname is already in the json file, return 403
    # else return 200
    room_server = read_json('room_server.json') # read database
    if roomname in room_server.keys():
        return 403
    else:
        room_server[roomname] = {}
        for day in range(1, 8):
            room_server[roomname][str(day)] = {}
            for hour in range(9, 18):
                room_server[roomname][str(day)][str(hour)] = False
        update_json('room_server.json', room_server) # update database
        return 200


def remove_room(roomname):
    # delete room from json file
    # if roomname is not in the json file, return 403
    # else return 200
    room_server = read_json('room_server.json') # read database
    if roomname not in room_server.keys():
        return 403
    else:
        del room_server[roomname]
        update_json('room_server.json', room_server) # update database
        return 200


def reserve_room(roomname, day, hour, duration):
    # reserve room in json file
    # if any of the input is invalid return 400
    # if room is already reserved return 403
    # else return 200
    room_server = read_json('room_server.json') # read database
    day, hour, duration = int(day), int(hour), int(duration)
    if roomname not in room_server.keys():
        return 400
    if int(day) not in range(1, 8):
        return 400
    if int(hour) not in range(9, 18):
        return 400
    if int(duration) not in range(1, 10):
        return 400
    for i in range(duration):
        if room_server[roomname][str(day)][str(hour + i)]:
            return 403
    for i in range(duration):
        room_server[roomname][str(day)][str(hour + i)] = True
    update_json('room_server.json', room_server) # update database
    return 200


def check_availability(roomname, day):
    # if roomname is not exists return 404, None
    # if day is not a valid day return 400, None
    # else return 200, "available hours"
    room_server = read_json('room_server.json') # read database
    if roomname not in room_server.keys():
        return 404, None
    if int(day) not in range(1, 8):
        return 400, None
    available_hours = []
    for hour in range(9, 18):
        if not room_server[roomname][day][str(hour)]:
            available_hours.append(hour)
    available_hours = " ".join(str(hour) for hour in available_hours)
    return 200, available_hours
    


#################### Activity Server ####################
def add_activity(activityname):
    # add activity to json file
    # if activityname is already in the json file, return 403
    # else return 200
    activity_server = read_json('activity_server.json') # read database
    if activityname in activity_server.keys():
        return 403
    else:
        activity_server[activityname] = {}
        update_json('activity_server.json', activity_server) # update database
        return 200

def remove_activity(activityname):
    # delete activity from json file
    # if activityname is not in the json file, return 403
    # else return 200
    activity_server = read_json('activity_server.json') # read database
    if activityname not in activity_server.keys():
        return 403
    else:
        del activity_server[activityname]
        update_json('activity_server.json', activity_server) # update database
        return 200


def check_activity(activityname):
    # check if activity is in json file
    # if activityname is not in the json file, return 404
    # else return 200
    activity_server = read_json('activity_server.json') # read database
    if activityname not in activity_server.keys():
        return 404
    
    return 200
    
def add_reservation(activityname, roomname, day, hour, duration):
    # add reservation to json file
    # if any of the input is invalid return 400
    activity_server = read_json('activity_server.json') # read database
    activity_server[activityname]["room"] = roomname
    activity_server[activityname]["day"] = day
    activity_server[activityname]["hour"] = hour
    activity_server[activityname]["duration"] = duration
    update_json('activity_server.json', activity_server) # update database
    
def generate_reservation_id():
    # generate a unique reservation_id
    # return reservation_id
    reservation_server = read_json('reservation_server.json') # read database
    if len(reservation_server) == 0:
        return 1
    else:
        int_keys = [int(key) for key in reservation_server.keys()]
        max_num = max(int_keys)
        return max_num + 1

def add_reservation_id(reservation_id, activityname):
    # add reservation to json file
    reservation_server = read_json('reservation_server.json') # read database
    reservation_server[reservation_id] = activityname
    update_json('reservation_server.json', reservation_server) # update database
    
    
def reservation_reserve(roomname, activityname, day, hour, duration):
    # reserve room in json file
    # create reservation_id (should be unique)
    # return 200, reservation_id
   
    add_reservation(activityname, roomname, day, hour, duration)
    reservation_id = generate_reservation_id()
    add_reservation_id(reservation_id, activityname)
    return 200, reservation_id

def display_reservation(reservation_id):
    # display reservation information from the json file
    # if reservation_id does not exits return 404, None
    # else return 200, reservation information
    reservation_server = read_json('reservation_server.json') # read database
    activity_server = read_json('activity_server.json') # read database
    if reservation_id not in reservation_server.keys():
        return 404, None
    else:
        activityname = reservation_server[reservation_id]
        roomname = activity_server[activityname]["room"]
        day = activity_server[activityname]["day"]
        hour = activity_server[activityname]["hour"]
        duration = activity_server[activityname]["duration"]
        update_json('reservation_server.json', reservation_server) # update database
        update_json('activity_server.json', activity_server) # update database

        return 200, roomname + "," + activityname + "," + str(day) + "," + str(hour) + "," + str(duration)


def read_json(filename):
    with open(filename, "r") as f:
        return json.load(f)
    
def update_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
def create_json(filename):
    with open(filename, "w") as f:
        json.dump({}, f, indent=4)
            
def create_databse_folders():
    create_json('room_server.json')
    create_json('activity_server.json')
    create_json('reservation_server.json')

create_databse_folders()