import json

#################### Room Server ####################
def add_room(roomname):
    # add room to json file
    # if roomname is already in the json file, return 403
    # else return 200
    if roomname in room_server.keys():
        return 403
    else:
        room_server[roomname] = {}
        for day in range(7):
            room_server[roomname][str(day)] = {}
            for hour in range(9, 18):
                room_server[roomname][str(day)][str(hour)] = False
        return 200


def remove_room(roomname):
    # delete room from json file
    # if roomname is not in the json file, return 403
    # else return 200
    if roomname not in room_server.keys():
        return 403
    else:
        del room_server[roomname]
        return 200


def reserve_room(roomname, day, hour, duration):
    # reserve room in json file
    # if any of the input is invalid return 400
    # if room is already reserved return 403
    # else return 200
    if roomname not in room_server.keys():
        return 400
    if day not in range(7):
        return 400
    if hour not in range(9, 18):
        return 400
    if duration not in range(1, 10):
        return 400
    for i in range(duration):
        if room_server[roomname][str(day)][str(hour + i)]:
            return 403
    for i in range(duration):
        room_server[roomname][str(day)][str(hour + i)] = True
    return 200


def check_availability(roomname, day):
    # if roomname is not exists return 404, None
    # if day is not a valid day return 400, None
    # else return 200, "available hours"
    if roomname not in room_server.keys():
        return 404, None
    if int(day) not in range(7):
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
    if activityname in activity_server.keys():
        return 403
    else:
        activity_server[activityname] = {}
        return 200

def remove_activity(activityname):
    # delete activity from json file
    # if activityname is not in the json file, return 403
    # else return 200
    if activityname not in activity_server.keys():
        return 403
    else:
        del activity_server[activityname]
        return 200


def check_activity(activityname):
    # check if activity is in json file
    # if activityname is not in the json file, return 404
    # else return 200
    if activityname not in activity_server.keys():
        return 404
    
    return 200
    
def add_reservation(activityname, roomname, day, hour, duration):
    # add reservation to json file
    # if any of the input is invalid return 400
    
    activity_server[activityname]["room"] = roomname
    activity_server[activityname]["day"] = day
    activity_server[activityname]["hour"] = hour
    activity_server[activityname]["duration"] = duration

def generate_reservation_id():
    # generate a unique reservation_id
    # return reservation_id
    if len(reservation_server) == 0:
        return 1
    else:
        return max(reservation_server.keys()) + 1

def add_reservation(reservation_id, activityname):
    # add reservation to json file
    
    reservation_server[reservation_id] = activityname

def reservation_reserve(roomname, activityname, day, hour, duration):
    # reserve room in json file
    # create reservation_id (should be unique)
    # return 200, reservation_id
   
    add_reservation(activityname, roomname, day, hour, duration)
    reservation_id = generate_reservation_id()
    add_reservation(reservation_id, activityname)
    return 200, reservation_id

def display_reservation(reservation_id):
    # display reservation information from the json file
    # if reservation_id does not exits return 404, None
    # else return 200, reservation information
    
    if reservation_id not in reservation_server.keys():
        return 404, None
    else:
        activityname = reservation_server[reservation_id]
        roomname = activity_server[activityname]["room"]
        day = activity_server[activityname]["day"]
        hour = activity_server[activityname]["hour"]
        duration = activity_server[activityname]["duration"]
        return 200, roomname + "," + activityname + "," + str(day) + "," + str(hour) + "," + str(duration)

with open("room_server.json", "r") as f:
    room_server = json.load(f)

with open("activity_server.json", "r") as f:
    activity_server = json.load(f)

with open("reservation_server.json", "r") as f:
    reservation_server = json.load(f)