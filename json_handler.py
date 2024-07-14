import json

from exceptions import BadRequest, Forbidden, NotFound
from models import DisplayReservation, Room

ROOM_INPUT_PATH = "data/room_server.json"
ACTIVITY_INPUT_PATH = "data/activity_server.json"
RESERVATION_INPUT_PATH = "data/reservation_server.json"


#################### Room Server ####################
def add_room(roomname: str):
    # add room to json file
    # if roomname is already in the json file, return 403
    # else return 200
    room_server = read_json(ROOM_INPUT_PATH)
    if roomname in room_server.keys():
        raise Forbidden(body=f"Room with name {roomname} is already in the list.")

    room = Room(name=roomname)
    room_server[room.name] = room.days

    update_json(ROOM_INPUT_PATH, room_server)
    return True


def remove_room(roomname: str):
    # delete room from json file
    # if roomname is not in the json file, return 403
    # else return 200
    room_server = read_json(ROOM_INPUT_PATH)
    if roomname not in room_server.keys():
        raise Forbidden(body=f"Room with name {roomname} is not found.")

    del room_server[roomname]
    update_json(ROOM_INPUT_PATH, room_server)
    return True


def reserve_room(roomname: str, day: int, hour: int, duration: int):
    # reserve room in json file
    # if room is already reserved raise Forbidden
    # else return 200

    room_server = read_json(ROOM_INPUT_PATH)
    if roomname not in room_server.keys():
        raise BadRequest(body="Invalid Input.")

    for i in range(duration):
        if room_server[roomname][str(day)][str(hour + i)]:
            raise Forbidden(body=f"Room {roomname} is already reserved.")

    for i in range(duration):
        room_server[roomname][str(day)][str(hour + i)] = True

    update_json(ROOM_INPUT_PATH, room_server)
    return True


def check_availability(roomname: str, day: int): # if: int roomname is not exists raise NotFound
    # else return 200, "available hours"
    room_server = read_json(ROOM_INPUT_PATH)
    if roomname not in room_server.keys():
        raise NotFound(body=f"Room {roomname} does not exists.")

    available_hours = []
    for hour in range(9, 18):
        if not room_server[roomname][str(day)][str(hour)]:
            available_hours.append(hour)
    available_hours = " ".join(str(hour) for hour in available_hours)

    return available_hours


#################### Activity Server ####################
def add_activity(activityname: str):
    # add activity to json file
    # if activityname is already in the json file, raise Forbidden
    # else return 200
    activity_server = read_json(ACTIVITY_INPUT_PATH)
    if activityname in activity_server.keys():
        raise Forbidden(
            body=f"Activity with name {activityname} is already in the list."
        )

    activity_server[activityname] = {}
    update_json(ACTIVITY_INPUT_PATH, activity_server)
    return True


def remove_activity(activityname: str):
    # delete activity from json file
    # if activityname is not in the json file, raise Forbidden
    # else return 200
    activity_server = read_json(ACTIVITY_INPUT_PATH)
    if activityname not in activity_server.keys():
        raise Forbidden(body=f"Activity with name {activityname} does not found.")

    del activity_server[activityname]
    update_json(ACTIVITY_INPUT_PATH, activity_server)
    return True


def check_activity(activityname: str):
    # check if activity is in json file
    # if activityname is not in the json file, return 404
    # else return 200
    activity_server = read_json(ACTIVITY_INPUT_PATH)
    if activityname not in activity_server.keys():
        raise NotFound(body=f"Activity with name {activityname} is not found.")

    return True


def add_reservation(activityname: str, roomname:str, day: int, hour: int, duration: int):
    # add reservation to json file
    # if any of the input is invalid return 400
    activity_server = read_json(ACTIVITY_INPUT_PATH)
    activity_server[activityname] = {
        "room": roomname,
        "day": day,
        "hour": hour,
        "duration": duration,
    }
    update_json(ACTIVITY_INPUT_PATH, activity_server)


def generate_reservation_id():
    # generate a unique reservation_id
    # return reservation_id
    reservation_server = read_json(RESERVATION_INPUT_PATH)
    if len(reservation_server) == 0:
        return 1
    else:
        int_keys = [int(key) for key in reservation_server.keys()]
        max_num = max(int_keys)
        return max_num + 1


def add_reservation_id(reservation_id: int, activityname: str):
    # add reservation to json file
    reservation_server = read_json(RESERVATION_INPUT_PATH)
    reservation_server[reservation_id] = activityname
    update_json(RESERVATION_INPUT_PATH, reservation_server)


def reservation_reserve(roomname: str, activityname, day: int, hour: int, duration: int):
    # reserve room in json file
    # create reservation_id (should be unique)
    # return 200, reservation_id

    add_reservation(activityname, roomname, day, hour, duration)
    reservation_id = generate_reservation_id()
    add_reservation_id(reservation_id, activityname)
    return 200, reservation_id


def display_reservation(reservation_id: str):
    # display reservation information from the json file
    # if reservation_id does not exits raise NotFound
    # else return 200, reservation information
    reservation_server = read_json(RESERVATION_INPUT_PATH)
    activity_server = read_json(ACTIVITY_INPUT_PATH)
    if reservation_id not in reservation_server.keys():
        raise NotFound(body=f"Reservation with {reservation_id} id does not exist.")

    activity_name = reservation_server.get(reservation_id)
    activity_data = activity_server[activity_name]
    response = DisplayReservation(activity=activity_name, **activity_data)

    update_json(RESERVATION_INPUT_PATH, reservation_server)
    update_json(ACTIVITY_INPUT_PATH, activity_server)

    return response.text


def read_json(filename: str):
    with open(filename, "r") as f:
        return json.load(f)


def update_json(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def create_json(filename: str):
    with open(filename, "w") as f:
        json.dump({}, f, indent=4)


def create_databse_folders():
    create_json("data/room_server.json")
    create_json("data/activity_server.json")
    create_json("data/reservation_server.json")


create_databse_folders()
