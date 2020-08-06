import datetime

class Log():
    def __init__(self, logline):
        data = logline.split()
        start = data[1] + ' ' + data[2]
        end = data[3] + ' ' + data[4]
        self._tempID = data[0]
        self._startdt = datetime.datetime.strptime(start, "%d/%m/%Y %H:%M:%S")        
        self._enddt = datetime.datetime.strptime(end, "%d/%m/%Y %H:%M:%S")
    
    def tempID(self):
        return self._tempID

    def start(self):
        return self._startdt
    
    def end(self):
        return self._enddt
