from socket import *
import re
import json_handler

serverPort = 8002
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The Activity server is ready to receive', serverSocket.getsockname())