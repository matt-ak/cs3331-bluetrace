import time
import datetime as dt

RIGHT_P = 0
WRONG_P = 1
BLOCKED = 2


class User():
    def __init__(self, userID, password):
        self._userID = userID
        self._password = password
        self._currID = None
        self._loginAttempt = 0
        self._blocktime = None
        self._idLog = []
         
    def checkPass(self, password):
        return self._password == password

    def blocked(self, block_duration, password):
        print(self._loginAttempt)
        if (password != self._password):
            if self._loginAttempt == 3:
                timeSince = (dt.datetime.now() - self._blocktime)
                print("time since: " + str(timeSince.total_seconds))
                if timeSince.total_seconds() < block_duration:
                    return BLOCKED
                self._blocktime = dt.datetime.now()
                self._loginAttempt = 1
                return BLOCKED
            else:
                self._loginAttempt += 1
                if (self._loginAttempt == 3):
                    self._blocktime = dt.datetime.now()
                return WRONG_P
        self._loginAttempt = 0
        self._blocktime = None
        return RIGHT_P

    def set_address(self, address):
        self._clientAddress = address
    
    def address(self):
        return self._clientAddress

    def userID(self):
        return self._userID

    