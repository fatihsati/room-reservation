from socket import *

serverName = 'localhost'
serverPort = 8001

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

# sentence = input('Write a roomname:/add?name=can')
sentence = 'GET /add?name=can HTTP/1.1\r'
clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(4096)
print('From Server:', modifiedSentence.decode())
# print('Socket name:', clientSocket.getsockname())
# print('Socket peer:', clientSocket.getpeername())

clientSocket.close()
