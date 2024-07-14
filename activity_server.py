

import json_handler
from exceptions import Forbidden, NotFound
from models import ActivityBase, HttpResponse
from utils import parse_input
from operations import OperationManager

from server_manager import Server


serverPort = 8001
serverSocket = Server('localhost', serverPort)
serverSocket.listen()
print("The Activity server is ready to receive", serverSocket.socket.getsockname())


def add_operation(input: ActivityBase) -> HttpResponse:
    try:
        status_code = json_handler.add_activity(input.name)
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
        title="Activity Added",
        body=f"Activity with name {input.name} is successfully added.",
    )


def remove_operation(input: ActivityBase) -> HttpResponse:
    try:
        status_code = json_handler.remove_activity(input.name)
    except Forbidden as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Error",
            body=e.message,
        )

    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Activity Removed",
        body=f"Activity with name {input.name} is successfully removed.",
    )


def check_operation(input: ActivityBase) -> HttpResponse:
    try:
        status_code = json_handler.check_activity(input.name)
    except NotFound as e:
        return HttpResponse(
            status_code=e.status_code,
            response_message=e.message,
            title="Error",
            body=e.body,
        )
    return HttpResponse(
        status_code=200,
        response_message="OK",
        title="Activity Found",
        body=f"Activity with name {input.name} is found.",
    )


operation_fn_mapping = {
    "add": add_operation,
    "remove": remove_operation,
    "check": check_operation,
}
input_cls_mapping = {"add": ActivityBase, "remove": ActivityBase, "check": ActivityBase}

operation_manager = OperationManager(
    fn_mappings=operation_fn_mapping, input_cls_mappings=input_cls_mapping
)

while True:
    connectionSocket, addr = serverSocket.socket.accept()
    message = connectionSocket.recv(1024)
    print("Message received from: ", addr)
    operation, parameters = parse_input(message.decode())

    # if message is favicon.ico close the connection
    if operation is False:
        connectionSocket.close()
        continue

    html = operation_manager.create_HTML(operation, parameters)

    connectionSocket.send(html.encode())
    connectionSocket.close()
