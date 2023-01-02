from socket import *
import re
import json_handler

serverPort = 8000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
print('The Room server is ready to receive', serverSocket.getsockname())

days_dict = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}

def parse_room_server_message(message):
    
    connection_method = message.split(' ')[0]   # GET or POST
    
    if connection_method == 'POST':
        data = re.search(r'{([\s\S]*?)}', message).group(1) # get the data between { and } from the message.
        data = data.replace('"', '')    # since the data is in the form of "operation: add, name: room1", we need to remove the " from the data.
        parameters = {}
        for key, value in [parameter.split(':') for parameter in data.split(',')]:  # split data from comma and then split each part from colon
            # remove the spaces from the key and value
            parameters[key.strip()] = value.strip()
        
        try:
            operation = parameters['operation']
        except:
            return None, None   # operation is not found
        return parameters['operation'], parameters
    
    # if connection method is GET
    # get the url from header
    print(message)
    requested_url = message.split(' ')[1]
    if requested_url == '/favicon.ico':
        return False, None
    
    # parse operation and roomname
    # split the url http://localhost:12000/add?name=fatih to a dictionary where key is operation add and value is roomname fatih
    try:
        operation= requested_url.split('?')[0].split('/')[-1]
        
        parameters = {}
        
        parameters_part = requested_url.split('?')[1]
        splitted_parameters = parameters_part.split('&')
        
        for key, value in [parameter.split('=') for parameter in splitted_parameters]:
            parameters[key] = value
    except:
        return None, None   # None,None means that the url is not valid. add?nameroom1 will return None, None since it has no "=" in it. 
    
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
    if status_code == 200:
        start_hour = int(hour)
        end_hour = int(hour) + int(duration)
        title_message = 'Reservation Successful'
        body_message = f" Room {roomname} is reserved at {days_dict[day]}, {start_hour}:00 - {end_hour}:00."
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
        try:
            name = parameters['name']
        except:
            return None
        title_message, body_message, status_code, response_message = add_operation(name)
    
    elif operation == 'remove':
        try:
            name = parameters['name']
        except:
            return None
        title_message, body_message, status_code, response_message = remove_operation(name)
    
    elif operation == 'reserve':
        try:
            roomname, day, hour, duration = parameters['name'], parameters['day'], parameters['hour'], parameters['duration']
        except:
            return None
        title_message, body_message, status_code, response_message = reserve_operation(roomname, day, hour, duration)
    
    elif operation == 'checkavailability':
        try:
            name, day = parameters['name'], parameters['day']
        except:
            return None
        title_message, body_message, status_code, response_message =  check_availability_operation(name, day)
    
    else:
        title_message = 'Error'
        body_message = "Invalid operation."
        status_code = 404
        response_message = 'Not Found'
    
    html = f"HTTP/1.1 {status_code} {response_message}\r\n\n<HTML> <HEAD> <TITLE>{title_message}</TITLE> </HEAD> <BODY>{body_message}</BODY> </HTML>"
    return html

def create_error_message():
    title_message = 'Error'
    body_message = 'Invalid Input'
    status_code = 400
    response_message = 'Bad Request'
    html = f"HTTP/1.1 {status_code} {response_message}\r\n\n<HTML> <HEAD> <TITLE>{title_message}</TITLE> </HEAD> <BODY>{body_message}</BODY> </HTML>"
    return html


while True:
    
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(1024)
    
    # print(f'Message is received from {addr}. Message is {message.decode()}')
    print(f'Message is received from {addr}.')

    operation, parameters = parse_room_server_message(message.decode())
    if operation is False:   # if message is favicon.ico close the connection
        connectionSocket.close()
        continue

    if operation is None:   # if operation is None, it means that the message is not valid
        connectionSocket.send(create_error_message().encode())  # send error message, wait for next request
        connectionSocket.close()
        continue
    
    html = create_HTML(operation, parameters)
    
    if html == None:    # parameters are not valid
        connectionSocket.send(create_error_message().encode())
        connectionSocket.close()
        continue
    
    connectionSocket.send(html.encode())
    connectionSocket.close()
