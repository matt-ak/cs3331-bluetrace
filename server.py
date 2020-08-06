#!python3
"""
Fair warning to whoever is reading this file: this is likely far from a good
solution to the specification, don't use this to cheat
"""

import datetime as dt
from socket import *
import sys
import threading
from _thread import *
import time
from user import *
import json
from random import randint
from log import Log

BUFSIZE = 2048
blockDuration = 0
serverPort = 0
credentials = {}
clientSocket = socket(AF_INET, SOCK_STREAM)
serverSocket = socket(AF_INET, SOCK_STREAM)
activeThreads = []
t_lock = threading.Lock()

def server():
    print("server is ready to recieve")
    serverSocket.listen(10)
    while(1):
        print("Waiting for connection")
        cSocket, (addr, port) = serverSocket.accept()
        
        print("Client connected: " + addr)

        start_new_thread(threaded, (cSocket, ))

# TODO: FIX THE LOCKS
def threaded(cSocket):
    while True:
        flag = False
        login = recvJSON(cSocket)
        if (login["type"] != "login"):
            print("Client error")
            continue
        # t_lock.acquire()
        user = credentials.get(login["userID"])
        if (user is None):
            message = {"type": "login", "result": "userID failed"}
            sendJSON(message, cSocket)
            continue
        status = user.blocked(blockDuration, login["password"])
        if (status == WRONG_P):
            message = {"type": "login", "result": "password failed"}
        elif (status == BLOCKED):
            message = {"type": "login", "result": "blocked"}
        elif (status == RIGHT_P):
            flag = True
            message = {"type": "login", "result": "success"}
        # t_lock.release()
        sendJSON(message, cSocket)

        if (flag):
            handle_commands(cSocket, user)
            break

    cSocket.close()

def handle_commands(cSocket, user):
    while True:
        messageDict = recvJSON(cSocket)
        if (messageDict["type"] == "download"):
            generate_ID(cSocket, user)
        elif (messageDict["type"] == "upload"):
            receive_log(cSocket)
        elif (messageDict["type"] == "logout"):
            logout(cSocket, user)
            break
        else:
            print("Client error")

def sendJSON(message, cSocket):
    cSocket.send(json.dumps(message).encode('utf-8'))

def recvJSON(cSocket):
    message = cSocket.recv(BUFSIZE)
    return json.loads(message.decode('utf-8'))

def generate_ID(cSocket, user):
    tempID = str(randint(0, 9))
    for i in range(19):
        tempID += str(randint(0, 9))
    print("New tempID: " + tempID)
    message = {"type": "tempID", "tempID": tempID}
    tempIDFile = open("tempIDs.txt", 'a+')
    current = dt.datetime.now()
    expiry = current + dt.timedelta(minutes=15)
    tempIDFile.write("\n{0} {1} {2} {3}".format(
        user.userID(), tempID, current.strftime("%d/%m/%Y %H:%M:%S"), 
        expiry.strftime("%d/%m/%Y %H:%M:%S")))
    sendJSON(message, cSocket)
    
def receive_log(cSocket):
    message = {"type": "upload"}
    sendJSON(message, cSocket)
    # TODO: Change file name back
    logFile = open("contactlog.txt", 'wb')
    message = cSocket.recv(BUFSIZE)
    logFile.write(message)
    while(message):
        message = cSocket.recv(BUFSIZE)
        if (message.decode() == "complete"):
            break
        logFile.write(message)
    logFile.close()
    sendJSON({"type": "success"}, cSocket)
    logs = parse_log()
    contact_trace(logs)
    

def parse_log():
    # TODO THIS AS WELL
    logFile = open("contactlog.txt", 'r')
    lines = logFile.readlines()
    logs = [Log(line) for line in lines]
    logFile.close()
    return logs
    
def contact_trace(logs):
    curr = dt.datetime.now()
    for log in logs:
        if log.start() < curr and log.end() > curr:
            user = find_user(log)

def find_user(log):
    pass
    tempIDFile = open("tempIDs.txt", "r")
    lines = tempIDFile.readlines()
    for line in lines:
        things = line.split()
        if (log.tempID == things[1]):
            print("{0} {1} {2}".format(things[1], things[2], things[3]))


def logout(cSocket, user):
    sendJSON({"type": "logout"}, cSocket)
    print("User has been logged out: " + user.userID())

def main():
    global blockDuration
    global serverPort
    global credentials
    global serverSocket

    if (len(sys.argv) != 3):
        print("Usage is: python3 server.py <port> <block_duration>")
        exit(-1)
    
    serverPort = int(sys.argv[1])
    blockDuration = int(sys.argv[2])

    # Read the user list from "credentials.txt" into a dictionary "credentials"
    credFile = open("credentials.txt", 'r')
    lines = credFile.readlines()
    lines = list(map(lambda x: x.split(), lines))
    credentials = {lines[i][0]: User(lines[i][0], lines[i][1]) for i in range(len(lines))}

    # Reading the existing tempIDs into the users
    tempsFile = open("tempIDs.txt", 'r')
    lines = tempsFile.readlines()
    for line in lines:
        thing = line.split()
        if credentials.get(thing[0]) is not None:
            credentials.get(thing[0])

    
    serverSocket.bind(('localhost', serverPort))
    server()
    while True:
        time.sleep(0.1)

main()