import time
import threading

class Storage:
    def __init__(self):
        self.data = {}
        self.timestamp = {}
        self.maxSize = 2
        self.lock = threading.Lock()

    def add(self,name,way,datas):
        self.lock.acquire()
        if len(self.timestamp) > self.maxSize:
            min_key = min(self.timestamp, key=self.timestamp.get)
            del self.data[min_key]
            del self.timestamp[min_key]
        hashkey = name + "_" +  way
        self.data[hashkey] = datas
        self.timestamp[hashkey] = int(time.time())
        self.lock.release()
    
    def get(self,name,way):
        hashkey = name + "_" +  way
        if self.timestamp.__contains__(hashkey):
            if int(time.time()) - self.timestamp[hashkey] <= 100000:
                return self.data[hashkey]
            else:
                self.lock.acquire()
                del self.data[hashkey]
                del self.timestamp[hashkey]
                self.lock.release()
                return None
        else:
            return None

