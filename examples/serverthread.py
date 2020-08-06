import socket, threading

class ClientThread(threading.Thread):
    def __init__(self, address, port, socket, name):
        super().__init__(name=name)
        self.address = address
        self.port = port
        self.socket = socket
        print("New thread started for " + address + ", with name " + name)
    
    def run(self):
        print("Connected")