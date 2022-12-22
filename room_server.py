from socket import *
import re


serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The Room server is ready to receive', serverSocket.getsockname())

def parse_room_server_message(message):
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
        
    
    print(operation, parameters)
    return operation, parameters

def create_HTML(operation, parameters):

    html = f"HTTP/1.1 200 OK\r\n\n<HTML> <HEAD> <TITLE>Room {operation}</TITLE> </HEAD> <BODY> Room with name {parameters['name']} is successfully {operation}.</BODY> </HTML>"
    return html

while True:
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(1024)

    operation, roomname = parse_room_server_message(message.decode())
    html = create_HTML(operation, roomname)
    respone = f"\rHTTP/1.1 200 OK\r\n\nThe {operation} operation is recieved.\r\nRoom {roomname} is added.\r".encode()
    connectionSocket.send(html.encode())
    connectionSocket.close()

serverSocket.close()