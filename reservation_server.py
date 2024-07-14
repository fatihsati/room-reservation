from socket import *

import json_handler
from exceptions import NotFound
from models import (
    DisplayInput,
    HttpResponse,
    ListAvailabilityInput,
    RequestResponse,
    ReserveInput,
)
from utils import parse_input
from operations import OperationManager


serverPort = 8002
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("localhost", serverPort))
serverSocket.listen(1)
print("The Reservation server is ready to receive", serverSocket.getsockname())

days_dict = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}
servername_to_port = {"room": 8000, "activity": 8001}

room_not_exists_response = HttpResponse(
    status_code=404,
    response_message="Not Found",
    title="Not Found",
    body="Room does not exist.",
)


def send_request_to_another_server(servername, url_input) -> RequestResponse:
    serverPort = servername_to_port[servername]
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(("localhost", serverPort))
    message = f"GET /{url_input} HTTP/1.1\r"
    clientSocket.send(message.encode())
    response = clientSocket.recv(1024)
    response = response.decode()
    clientSocket.close()

    header, message = response.split("\r\n\n")

    response = RequestResponse(header=header, message=message)

    return response


def reserve_operation(input: ReserveInput):
    activity_response = send_request_to_another_server(
        "activity", f"check?name={input.activity}"
    )
    # activity server returns 404 if activity is not available
    if activity_response.status_code == 404:
        return HttpResponse(
            status_code=activity_response.status_code,
            response_message="Not Found",
            title="Activity Not Exists",
            body=activity_response.body,
        )

    room_response = send_request_to_another_server(
        "room",
        f"reserve?name={input.room}&day={input.day}&hour={input.hour}&duration={input.duration}",
    )

    # if room is available it retuns 200, create reservation id and save the reservation in json file
    if room_response.status_code == 200:
        status_code, reservation_id = json_handler.reservation_reserve(
            input.room, input.activity, input.day, input.hour, input.duration
        )
        return HttpResponse(
            status_code=200,
            response_message="OK",
            title="Reservation Successful",
            body=f"Room {input.room} is reserved for activity {input.activity} on {days_dict[str(input.day)]} at {input.hour}:00 for {input.duration} hours.\nYour reservation id is {reservation_id}.",
        )
    # if inputs are not valid, room server returns 400
    elif room_response.status_code == 400:
        return HttpResponse(
            status_code=room_response.status_code,
            response_message=room_response.response_message,
            title=room_response.title,
            body="Invalid input is given.",
        )
    # if room is not available, room server returns 404
    return HttpResponse(
        status_code=room_response.status_code,
        response_message="Forbidden",
        title="Forbidden",
        body=f"Room {input.room} is already reserved.",
    )


def listavailability_operation(input: ListAvailabilityInput):
    if input.day:
        response = send_request_to_another_server(
            "room", f"checkavailability?name={input.room}&day={input.day}"
        )
        if response.status_code == 404:
            return room_not_exists_response

        return HttpResponse(
            status_code=response.status_code,
            title=response.title,
            response_message=response.response_message,
            body=response.body,
        )
    body = ""
    # get response for all days and update body
    for day in range(1, 8):
        response = send_request_to_another_server(
            "room", f"checkavailability?name={input.room}&day={day}"
        )
        if response.status_code == 404:
            return room_not_exists_response

        body += f"On {days_dict[str(day)]}: {response.body} <br>"

    return HttpResponse(
        status_code=response.status_code,
        title=response.title,
        response_message=response.response_message,
        body=body,
    )


def display_operation(input: DisplayInput):
    try:
        response = json_handler.display_reservation(input.id)
    except NotFound as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Reservation Not Found",
            body=e.body,
        )

    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Reservation Information",
        body=response,
    )


operation_fn_mapping = {
    "reserve": reserve_operation,
    "listavailability": listavailability_operation,
    "display": display_operation,
}

input_cls_mapping = {
    "reserve": ReserveInput,
    "listavailability": ListAvailabilityInput,
    "display": DisplayInput,
}

operation_manager = OperationManager(
    fn_mappings=operation_fn_mapping, input_cls_mappings=input_cls_mapping
)

while True:
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(1024)
    print("message received from: ", addr)
    operation, parameters = parse_input(message.decode())

    if operation is False:  # if operation is /favicon.ico, wait for next request
        connectionSocket.close()
        continue

    html = operation_manager.create_HTML(operation, parameters)

    connectionSocket.send(html.encode())
    connectionSocket.close()
