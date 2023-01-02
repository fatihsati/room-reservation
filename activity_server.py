from socket import *
import re
import json_handler

serverPort = 8001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
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
        return operation, parameters
    
    # get the url from header
    requested_url = message.split(' ')[1]
    if requested_url == '/favicon.ico':
        # example /favicon.ico message
       return False, None
        # requested_url = re.search(r'Referer: (.*)', message).group(1).split('/')[-1]
    
    # parse operation and roomname
    # split the url http://localhost:12000/add?name=fatih to a dictionary where key is operation add and value is roomname fatih
    try:
        operation= requested_url.split('?')[0].split('/')[-1]
        
        parameters = {}
        # split the url to a dictionary where key day and value is the day number
        
        parameters_part = requested_url.split('?')[1]
        splitted_parameters = parameters_part.split('&')
        
        for key, value in [parameter.split('=') for parameter in splitted_parameters]:
            parameters[key] = value
    except:
        return None, None
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
    
    elif operation == 'check':
        try:
            name = parameters['name']
        except:
            return None
        title_message, body_message, status_code, response_message = check_operation(name)
    
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
    print('Message received from: ', addr)
    operation, parameters = parse_activity_server_message(message.decode())
    
    if operation is False:   # if message is favicon.ico close the connection
        connectionSocket.close()
        continue
    
    if operation is None:   # if operation is None, it means that the message is not valid
        connectionSocket.send(create_error_message().encode())  # send error message, wait for next request
        connectionSocket.close()
        continue
    
    html = create_HTML(operation, parameters)
    
    if html is None:    # parameters are not valid
        connectionSocket.send(create_error_message().encode())
        connectionSocket.close()
        continue
    
    connectionSocket.send(html.encode())
    connectionSocket.close()
    
    