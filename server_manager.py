from socket import *

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
    
    def listen(self):
        self.socket.listen(1)

