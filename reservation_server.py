from socket import *
import re
import json_handler

serverPort = 8002
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
print('The Reservation server is ready to receive', serverSocket.getsockname())

servername_to_port = {'room': 8000,
                      'activity': 8001}

def send_request_to_another_server(servername, url_input):
    # create a socket and connect to the server
    # send the request to the server
    # get the response from the server
    # close the socket
    # return the response

    serverPort = servername_to_port[servername]
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(('localhost', serverPort))
    message = f"GET /{url_input} HTTP/1.1\r"
    clientSocket.send(message.encode())
    response = clientSocket.recv(4096)
    response = response.decode()
    clientSocket.close()
    return response

def parse_reservation_server_message(message):
    # get the url from header
    requested_url = message.split(' ')[1]
    if requested_url == '/favicon.ico':
        # requested_url = re.search(r'Referer: (.*)', message).group(1).split('/')[-1]
        return False, None
    
    # parse operation and roomname
    # split the url http://localhost:12000/add?name=fatih to a dictionary where key is operation add and value is roomname fatih
    try:
        operation= requested_url.split('?')[0].split('/')[-1]
        
        parameters = {}
        # get name if operation is add or remove

        parameters_part = requested_url.split('?')[1]
        splitted_parameters = parameters_part.split('&')
        
        for key, value in [parameter.split('=') for parameter in splitted_parameters]:
            parameters[key] = value
    except:
        return None, None
    return operation, parameters
    
def reserve_operation(roomname, activityname, day, hour, duration):
    # check if activity is available using activity server  (will be done in reservation server)
    # if activity is not available return 404
    # else: 
    # check if room available using room server, reserve it and return 200, save the reservation in json file and create a reservation_id
    # if room is not available return 404, if input is not valid return 400 (room server will return same status codes)
    # determine the status codes and write new if statements for them
    
    activity_check_response = send_request_to_another_server('activity', f'check?name={activityname}')
    response_status_code = int(activity_check_response.split(' ')[1])   # get the status code from the response
    if response_status_code == 404:  # activity server returns 404 if activity is not available
        title_message = 'Activity Not Exists'
        body_message = f"Activity {activityname} does not exist."
        response_message = 'Not Found'
        return title_message, body_message, response_status_code, response_message      # return the response to the client

    # check if room is available    add room using room add server, if it cannot add, it will return the corresponding status code
    # if status code returns 200, create a reservation id and save the reservation in json file
    # reservation will be saved to json file in the room server, no need to save it here
    
    room_check_response = send_request_to_another_server('room', f'reserve?name={roomname}&day={day}&hour={hour}&duration={duration}')
    room_status_code = int(room_check_response.split(' ')[1])
    # if room is available it retuns 200, create reservation id and save the reservation in json file
    if room_status_code == 200: # all conditions are met
        status_code, reservation_id = json_handler.reservation_reserve(roomname, activityname, day, hour, duration)
        title_message = 'Reservation Successful'
        body_message = f'Room {roomname} is reserved for activity {activityname} on {day} at {hour} for {duration} hours.\nYour reservation id is {reservation_id}.'
        response_message = 'OK'
        
    # if inputs are not valid, room server returns 400
    elif room_status_code == 400:
        title_message = 'Error'
        body_message = f" Invalid input is given."
        response_message = 'Bad Request'
    
    # if room is not available, room server returns 404
    else:
        title_message = 'Forbidden'
        body_message = f" Room {roomname} is already reserved."
        response_message = 'Forbidden'

    return title_message, body_message, room_status_code, response_message

def listavailability_operation(roomname, day):

    roomname_response = send_request_to_another_server('room', f'checkavailability?name={roomname}&day={day}')
    header, message = roomname_response.split('\r\n\n')

    room_status_code = int(header.split(' ')[1])
    room_response_message = header.split(' ')[2]
    # get room server response, parse it and return the response to the client
    title_message = re.search(r'<TITLE>(.*)<\/TITLE>', message).group(1)
    body_message = re.search(r'<BODY>(.*)<\/BODY>', message).group(1)
    
        
    return title_message, body_message, room_status_code, room_response_message

def display_operation(reservation_id):
    #//TODO: day should be converted to Monday, Tuesday... 
    #//TODO: # day, hour, duration should change to: "When: Friday 10:00-11:00" 
    
    status_code, reservation_information = json_handler.display_reservation(reservation_id)
    
    if status_code == 200:
        
        roomname, activityname, day, hour, duration = reservation_information.split(',')
        title_message = 'Reservation Information'
        body_message = f'Room: {roomname}\nActivity: {activityname}\nDay: {day}\nHour: {hour}\nDuration: {duration}'
        response_message = 'OK'
        
    else:
        title_message = 'Reservation Not Found'
        body_message = f'Reservation with {reservation_id} id does not exist.'
        response_message = 'Not Found'
        
    return title_message, body_message, status_code, response_message

def create_HTML(operation, parameters):
    
    if operation == 'reserve':
        roomname, activityname, day, hour, duration = parameters['room'], parameters['activity'], parameters['day'], parameters['hour'], parameters['duration']
        title_message, body_message, status_code, response_message = reserve_operation(roomname, activityname, day, hour, duration)
    
    elif operation == 'listavailability':
        if 'day' in parameters: # if day is given, list availability for that day
            roomname, day = parameters['room'], parameters['day']
            title_message, body_message, status_code, response_message = listavailability_operation(roomname, day)
        else: # if day is not given, list availability for all days
            final_body_message = '' # send connection for each day, get the response and add it to final_body_message
            roomname = parameters['room']
            for i in range(1, 8):   # check availability for all days
                title_message, body_message, status_code, response_message = listavailability_operation(roomname, i)
                final_body_message += f'On day {i}: {body_message} <br>'
            body_message = final_body_message
    elif operation == 'display':
        title_message, body_message, status_code, response_message = display_operation(parameters['id'])
    
    
    html = f"HTTP/1.1 {status_code} {response_message}\r\n\n<HTML>\n<HEAD>\n<TITLE>{title_message}</TITLE>\n</HEAD>\n<BODY>{body_message}</BODY>\n</HTML>"
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
    message = connectionSocket.recv(4096)
    operation, roomname = parse_reservation_server_message(message.decode())
    if not operation:   # if operation is /favicon.ico, wait for next request
        connectionSocket.close()
        continue
    if operation == None:
        connectionSocket.send(create_error_message().encode())  # send error message, wait for next request
        connectionSocket.close()
        continue
    html = create_HTML(operation, roomname)
    connectionSocket.send(html.encode())
    connectionSocket.close()