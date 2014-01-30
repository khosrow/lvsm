"""
Dummy module that simulates snimpy functionality on Keepalived 
for unit testing
"""
# The following vip/rip are hardcoded into the dummy module
# TCP  82.94.164.162:80
#   -> 216.34.181.45:80
#   -> 173.194.43.3:80         
# UDP  82.94.164.162:53
#   -> 208.67.222.222:53
#   -> 208.67.220.220:53
import socket

class TupleArray:
    def __init__(self):
        # prepare the real servers
        self.data = list(list())
        self.real.append([socket.inet_aton('216.34.181.45'), 
                          socket.inet_aton('173.194.43.3')])
        self.real.append([socket.inet_aton('208.67.222.222'),
                          socket.inet_aton('208.67.220.220')])
        
        self.port = list()
        self.port.append([80, 80])
        self.port.append([53, 53])

        self.weight = list()
        self.weight.append([1,1])
        self.weight.append([1,1])


class TupleArray:
    def __init__(self):
        # prepare the real servers
        self.data = list()

    def __setitem__(self, tup, value):
        i, j = tup
        print "stuff: %s" % len(self.data)
        if i >= 0 and i < len(self.data):
            if j >= 0 and j < len(self.data[i]):
                self.data[i][j] = value
            else:
                print "length: %s" % len(self.data[i])
                self.data[i].append(value)
        else:
            print "len: %s" % len(self.data)
            self.data.append([value])
        # p = self.data[i]

    def __getitem__(self, tup):
        i, j = tup
        return self.data[i][j]


class Manager(object):
    def __init__(self,
                 host='localhost', 
                 community='public',
                 version=2,
                 cache=False,
                 none=False,
                 timeout=None,
                 retries=None,
                 secname=None,
                 authprotocol=None,
                 authpassword=None,
                 privprotocol=None,
                 privpassword=None):
        """dummy init method"""
        self.virtualServerAddress = [socket.inet_aton('82.94.164.162'),
                                     socket.inet_aton('82.94.164.162')]
        self.virtualServerRealServersTotal = [2, 2]
        self.virtualServerPort = [80, 53]

        self.realServerAddress = TupleArray()
        self.realServerAddress[0,0] = socket.inet_aton('216.34.181.45')
        self.realServerAddress[0,1] = socket.inet_aton('173.194.43.3')
        self.realServerAddress[1,0] = socket.inet_aton('208.67.222.222')
        self.realServerAddress[1,1] = socket.inet_aton('208.67.220.220')

        self.realServerPort = TupleArray()
        self.realServerPort[0, 0] = 80
        self.realServerPort[0, 1] = 80
        self.realServerPort[1, 0] = 80
        self.realServerPort[1, 1] = 80

        self.realServerWeight = TupleArray()
        self.realServerWeight[0, 0] = 1
        self.realServerWeight[0, 1] = 1
        self.realServerWeight[1, 0] = 1
        self.realServerWeight[1, 1] = 1


def load(mibname):
    """Dummy load method"""
    pass