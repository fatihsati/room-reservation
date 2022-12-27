from socket import *
import re
import json_handler

serverPort = 8000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The Room server is ready to receive', serverSocket.getsockname())

def parse_room_server_message(message):
    print(message)
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

def add_operation(roomname):
    status_code = json_handler.add_room(roomname)
    if status_code == 200:   # if room is added
            title_message = 'Room Added'
            body_message = f" Room with name {roomname} is successfully added."
            response_message = 'OK'
    else:   # if room is already in the list
        title_message = 'Error'
        body_message = f" Room with name {roomname} is already in the list."
        response_message = 'Forbidden'

    return title_message, body_message, status_code, response_message

def remove_operation(roomname):
    status_code = json_handler.remove_room(roomname)
    if status_code == 200:   # if room is removed
        
        title_message = 'Room Removed'
        body_message = f" Room with name {roomname} is successfully removed."
        response_message = 'OK'
        
    else:
        title_message = 'Error'
        body_message = f" Room with name {roomname} is not found."
        response_message = 'Forbidden'
        
    return title_message, body_message, status_code, response_message

def reserve_operation(roomname, day, hour, duration):
    # TODO: convert day from 1-7 to monday-sunday
    # TODO: convert hour from 9-18 to 09:00-18:00
    
    status_code = json_handler.reserve_room(roomname, day, hour, duration)
    print(status_code)
    if status_code == 200:
        title_message = 'Reservation Successful'
        body_message = f" Room {roomname} is reserved at {day}, {hour} for {duration} hours."
        response_message = 'OK'
    elif status_code == 400:
        title_message = 'Error'
        body_message = f" Invalid input."
        response_message = 'Bad Request'
    else:
        title_message = 'Forbidden'
        body_message = f" Room {roomname} is already reserved."
        response_message = 'Forbidden'
    
    return title_message, body_message, status_code, response_message

def check_availability_operation(roomname, day):
    
    status_code, available_hours = json_handler.check_availability(roomname, day)
    
    if status_code == 200:
        title_message = 'Check Operation Successful'
        body_message = f" Room {roomname} is available for the following hours: {available_hours}."
        response_message = 'OK'
    elif status_code == 400:
        title_message = 'Error'
        body_message = f" Invalid input."
        response_message = 'Bad Request'
    else:
        title_message = 'Not Found'
        body_message = f" Room {roomname} does not exist."
        response_message = 'Not Found'
        
    return title_message, body_message, status_code, response_message

def create_HTML(operation, parameters):
    
    if operation == 'add':
        title_message, body_message, status_code, response_message = add_operation(parameters['name'])
    
    elif operation == 'remove':
        title_message, body_message, status_code, response_message = remove_operation(parameters['name'])
    
    elif operation == 'reserve':
        roomname, day, hour, duration = parameters['name'], parameters['day'], parameters['hour'], parameters['duration']
        title_message, body_message, status_code, response_message = reserve_operation(roomname, day, hour, duration)
    
    elif operation == 'checkavailability':
        title_message, body_message, status_code, response_message =  check_availability_operation(parameters['name'], parameters['day'])
    
    else:
        title_message = 'Error'
        body_message = "Invalid operation."
        status_code = 404
        response_message = 'Not Found'
    
    html = f"HTTP/1.1 {status_code} {response_message}\r\n\n<HTML> <HEAD> <TITLE>{title_message}</TITLE> </HEAD> <BODY>{body_message}</BODY> </HTML>"
    return html

while True:
    
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(1024)
    operation, parameters = parse_room_server_message(message.decode())
    html = create_HTML(operation, parameters)
    connectionSocket.send(html.encode())
    connectionSocket.close()
