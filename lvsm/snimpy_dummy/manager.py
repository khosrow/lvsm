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
        self.realServerAddress = []
        self.realServerWeight = []


def load(mibname):
    """Dummy load method"""
    pass