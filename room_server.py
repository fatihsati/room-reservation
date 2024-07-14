from socket import *

import json_handler
from exceptions import BadRequest, Forbidden, NotFound
from models import (
    BAD_REQUEST,
    HttpResponse,
    RoomBaseInput,
    RoomCheckAvailabilityInput,
    RoomReserveInput,
)
from utils import parse_input
from operations import OperationManager
from server_manager import Server

serverPort = 8000
serverSocket = Server("localhost", serverPort)
serverSocket.listen()
print("The Room server is ready to receive", serverSocket.getsockname())

days_dict = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def add_operation(input: RoomBaseInput) -> HttpResponse:
    try:
        result = json_handler.add_room(input.name)
    except Forbidden as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Error",
            body=e.body,
        )
    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Room Added",
        body=f"Room with name {input.name} is successfully added.",
    )


def remove_operation(input: RoomBaseInput) -> HttpResponse:
    try:
        status_code = json_handler.remove_room(input.name)
    except Forbidden as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Error",
            body=e.body,
        )
    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Room Removed",
        body=f"Room with name {input.name} is successfully removed.",
    )


def reserve_operation(input: RoomReserveInput) -> HttpResponse:
    try:
        status_code = json_handler.reserve_room(
            input.name, input.day, input.hour, input.duration
        )
    except BadRequest as e:
        return BAD_REQUEST

    except Forbidden as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Forbidden",
            body=e.body,
        )
    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Reservation Successful",
        body=f"Room {input.name} is reserved at {days_dict[str(input.day)]}, {input.hour}:00 - {int(input.hour) + int(input.duration)}:00.",
    )


def check_availability_operation(input: RoomCheckAvailabilityInput) -> HttpResponse:
    try:
        response = json_handler.check_availability(input.name, input.day)
    except NotFound as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Not Found",
            body=e.body,
        )

    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Check Operation Successful",
        body=f"Room {input.name} is available for the following hours: {response}.",
    )


operation_fn_mapping = {
    "add": add_operation,
    "remove": remove_operation,
    "reserve": reserve_operation,
    "checkavailability": check_availability_operation,
}

input_cls_mapping = {
    "add": RoomBaseInput,
    "remove": RoomBaseInput,
    "reserve": RoomReserveInput,
    "checkavailability": RoomCheckAvailabilityInput,
}

operation_manager = OperationManager(
    fn_mappings=operation_fn_mapping, input_cls_mappings=input_cls_mapping
)

while True:
    connectionSocket, addr = serverSocket.socket.accept()
    message = connectionSocket.recv(1024)

    print(f"Message is received from {addr}.")

    operation, parameters = parse_input(message.decode())
    # if message is favicon.ico close the connection
    if operation is False:
        connectionSocket.close()
        continue

    html = operation_manager.create_HTML(operation, parameters)

    connectionSocket.send(html.encode())
    connectionSocket.close()
