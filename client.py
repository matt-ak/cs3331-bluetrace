#!python3
"""
Client program for UNSW COMP3331 20T2
Usage: python3 client.py <server_ip> <server_port> <udp_port>

This program implements a thing
"""

from socket import *
import sys
import json
import time
from log import Log
from _thread import *

BUFSIZE = 2048

serverAddr = sys.argv[1]
serverPort = int(sys.argv[2])
udpPort = int(sys.argv[3])
tempID = 0

def sendJSON(message, cSocket):
    cSocket.send(json.dumps(message).encode('utf-8'))

def recvJSON(cSocket):
    message = cSocket.recv(BUFSIZE)
    return json.loads(message.decode('utf-8'))

def client(clientSocket, udpSocket):
    download_ID(clientSocket)
    print("tempID: " + str(tempID))

    # New thread to handle receiving beacons through udp socket
    start_new_thread(udpCentral, (udpSocket,))

    while True:
        command = input("Input command: ")
        if (command == "Download_tempID"):
            download_ID(clientSocket)
        elif (command == "Upload_contact_log"):
            upload_log(clientSocket)
        elif (command == "logout"):
            if logout(clientSocket):
                break
            else:
                print("Server error: unable to logout")
        else:
            args = command.split()
            if (args[0] == "Beacon"):
                beacon(udpSocket, args[1], args[2])
            else:
                print("Unknown command")

def upload_log(clientSocket):
    message = {"type": "upload"}
    sendJSON(message, clientSocket)
    response = recvJSON(clientSocket)
    if (response["type"] == "upload"):
        logs = open("z5206859_contactlog.txt", 'rb')
        clientSocket.sendfile(logs)
        time.sleep(1)
        clientSocket.send("complete".encode())
        response = recvJSON(clientSocket)
        if (response["type"] == "success"):
            print("Uploaded successfully")
            return
    else:
        print("Server error: unable to upload")

def logout(clientSocket):
    response = recvJSON(clientSocket)
    if response["type"] == "logout":
        print("Successfully logged out!")
        return True
    return False

def download_ID(clientSocket):
    global tempID
    messageDict = {"type": "download"}
    message = json.dumps(messageDict)
    clientSocket.send(message.encode('utf-8'))

    recvMessage = json.loads(clientSocket.recv(BUFSIZE).decode('utf-8'))
    if (recvMessage["type"] != "tempID"):
        print("server error")
        return
    tempID = recvMessage["tempID"]
    print("TempID: " + str(tempID))

def beacon(udpSocket, destIP, dest):
    while True:
        message = "{1} {2} {3} {4}".format(tempID, )


# Thread to do the udp receiving yeah
def udpCentral(thing):
    pass
    
def main():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverAddr, serverPort))

    udpSocket = socket(AF_INET, SOCK_DGRAM)
    udpSocket.bind(('localhost', udpPort))
    while True:
        userID = input("UserID: ")
        userPass = input("Password: ")

        messageDict = {"type": "login", "userID": userID, "password": userPass}
        message = json.dumps(messageDict)
        clientSocket.send(message.encode('utf-8'))

        receivedMessage = json.loads(clientSocket.recv(BUFSIZE))
        if receivedMessage["type"] == "login":
            if receivedMessage["result"] == "success":

                client(clientSocket, udpSocket)
                break
            elif receivedMessage["result"] == "blocked":
                print("Too many failed login attempts. Account is blocked")
            elif receivedMessage["result"] == "failed":
                print("Wrong password, try again")
            else:
                print("Server error")

    print(receivedMessage.decode('utf-8'))

main()
print("Program exited successfully")