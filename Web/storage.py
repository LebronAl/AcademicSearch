import time

class Storage:
    def __init__(self):
        self.data = {}
        self.timestamp = {}

    def add(self,name,way,datas):
        if len(self.timestamp) > 10000:
            min_key = min(self.timestamp.keys(), key=(lambda k: self.timestamp.keys[k])) 
            del self.data[min_key]
            del self.timestamp[min_key]
        print(datas)
        hashkey = name + "_" +  way
        self.data[hashkey] = datas
        self.timestamp[hashkey] = int(time.time())
    
    def get(self,name,way):
        hashkey = name + "_" +  way
        if self.timestamp.__contains__(hashkey):
            if int(time.time()) - self.timestamp[hashkey] <= 2:
                return self.data[hashkey]
            else:
                del self.data[hashkey]
                del self.timestamp[hashkey]
                return None
        else:
            return None

