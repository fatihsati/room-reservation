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
    #Standart message brwoser
    """GET /check?name=fatih HTTP/1.1
    Host: localhost:8001
    Connection: keep-alive
    sec-ch-ua: "Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"
    sec-ch-ua-mobile: ?0
    sec-ch-ua-platform: "Windows"
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Sec-Fetch-Site: none
    Sec-Fetch-Mode: navigate
    Sec-Fetch-User: ?1
    Sec-Fetch-Dest: document
    Accept-Encoding: gzip, deflate, br
    Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6"""
    # /favicon.ico message from browser
    """GET /favicon.ico HTTP/1.1
            Host: localhost:8001
            Connection: keep-alive
            sec-ch-ua: "Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"
            sec-ch-ua-mobile: ?0
            User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
            sec-ch-ua-platform: "Windows"
            Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8
            Sec-Fetch-Site: same-origin
            Sec-Fetch-Mode: no-cors
            Sec-Fetch-Dest: image
            Referer: http://localhost:8001/check?name=fatih
            Accept-Encoding: gzip, deflate, br
            Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6"""
    
    # get the url from header
    requested_url = message.split(' ')[1]
    if requested_url == '/favicon.ico':
        # example /favicon.ico message
       
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
    else:   # if activity is not found , status code is 404
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
    operation, parameters = parse_activity_server_message(message.decode())
    html = create_HTML(operation, parameters)
    connectionSocket.send(html.encode())
    connectionSocket.close()
    
    