from socket import *
import re
import json_handler

serverPort = 8001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The Activity server is ready to receive', serverSocket.getsockname())

def parse_activity_server_message(message):
    """get the decoded message, return operation and parameters
       Function is same with the room_server.py parse_room_server_message function"""
    # get the url from header
    requested_url = message.split(' ')[1]
    if requested_url == '/favicon.ico':
        requested_url = re.search(r'Referer: (.*)', message).group(1).split('/')[-1]
    
    # parse operation and roomname
    # split the url http://localhost:12000/add?name=fatih to a dictionary where key is operation add and value is roomname fatih
    operation= requested_url.split('?')[0].split('/')[-1]
    
    parameters = {}
    # get name if operation is add or remove
    if operation == 'add' or operation == 'remove':
        roomname = requested_url.split('=')[1]
        parameters['name'] = roomname
    
    # if operation is not add or remove, split the url to a dictionary where key day and value is the day number
    else:
        parameters_part = requested_url.split('?')[1]
        splitted_parameters = parameters_part.split('&')
        
        for key, value in [parameter.split('=') for parameter in splitted_parameters]:
            parameters[key] = value
        
    return operation, parameters

def add_operation(activityname):
    
    status_code = json_handler.add_activity(activityname)
    
    if status_code == 200:
        title_message = 'Activity Added'
        body_message = f" Activity with name {activityname} is successfully added."
        response_message = 'OK'
    else:
        title_message = 'Error'
        body_message = f" Activity with name {activityname} is already in the list."
        response_message = "Forbidden"
    
    return title_message, body_message, status_code, response_message

def remove_operation(activityname):
    status_code = json_handler.remove_activity(activityname)

    if status_code == 200:
        title_message = 'Activity Removed'
        body_message = f" Activity with name {activityname} is successfully removed."
        response_message = 'OK'
    else:
        title_message = 'Error'
        body_message = f" Activity with name {activityname} does not found."
        response_message = "Forbidden"

    return title_message, body_message, status_code, response_message

def check_operation(activityname):
    status_code = json_handler.check_activity(activityname)
    
    if status_code == 200:   # if activity is found
        title_message = 'Activity Found'
        body_message = f" Activity with name {activityname} is found."
        response_message = "OK"
    else:   # if activity is not found
        title_message = 'Error'
        body_message = f" Activity with name {activityname} is not found."
        response_message = 'Not Found'

    return title_message, body_message, status_code, response_message
        

def create_HTML(operation, parameters):
    
    if operation == 'add':
        title_message, body_message, status_code, response_message = add_operation(parameters['name'])
    
    elif operation == 'remove':
        title_message, body_message, status_code, response_message = remove_operation(parameters['name'])
    
    elif operation == 'check':
        title_message, body_message, status_code, response_message = check_operation(parameters['name'])
    
    html = f"HTTP/1.1 {status_code} {response_message}\r\n\n<HTML> <HEAD> <TITLE>{title_message}</TITLE> </HEAD> <BODY>{body_message}</BODY> </HTML>"
    return html

while True:
    
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(1024)
    operation, roomname = parse_activity_server_message(message.decode())
    html = create_HTML(operation, roomname)
    connectionSocket.send(html.encode())
    connectionSocket.close()
    
    