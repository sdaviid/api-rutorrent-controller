from datetime import datetime

class teste(object):
    def __init__(self):
        self.data = []
    def add_data(self):
        self.data.append(str(datetime.now().timestamp()))

n = teste()

def uau():
    return n