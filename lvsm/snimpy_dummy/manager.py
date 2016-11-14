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

# TCP  192.0.2.2:80  
#   -> 192.0.2.200:80
#   -> 192.0.2.201:80
# UDP  192.0.2.2:53  
#   -> 192.0.2.202:53
#   -> 192.0.2.203:53

import socket


class TupleArray:
    """A 2-D dictionary object"""
    def __init__(self):
        self.data = dict()

    def __setitem__(self, tup, value):
        i, j = tup
        try:
            self.data[int(i)][j] = value
        except KeyError:
            self.data[int(i)] = dict()
            self.data[int(i)][j] = value
    

    def __getitem__(self, tup):
        i, j = tup        
        return self.data[int(i)][j]


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
        self.virtualServerAddress = {'1': socket.inet_aton('192.0.2.2'),
                                     '2': socket.inet_aton('192.0.2.2')}
        self.virtualServerRealServersTotal = {'1': 2, '2': 2}
        self.virtualServerPort = {'1': 80, '2': 53}

        self.virtualServerProtocol = {'1': 'tcp', '2': 'udp'}

        self.realServerAddress = TupleArray()
        self.realServerAddress[1,1] = socket.inet_aton('192.0.2.200')
        self.realServerAddress[1,2] = socket.inet_aton('192.0.2.201')
        self.realServerAddress[2,1] = socket.inet_aton('192.0.2.202')
        self.realServerAddress[2,2] = socket.inet_aton('192.0.2.203')

        self.realServerPort = TupleArray()
        self.realServerPort[1, 1] = 80
        self.realServerPort[1, 2] = 80
        self.realServerPort[2, 1] = 53
        self.realServerPort[2, 2] = 53

        self.realServerWeight = TupleArray()
        self.realServerWeight[1, 1] = 1
        self.realServerWeight[1, 2] = 1
        self.realServerWeight[2, 1] = 1
        # Hardcoding zero to avoid warnings when running test_disablehost methods
        self.realServerWeight[2, 2] = 0


def load(mibname):
    """Dummy load method"""
    pass
