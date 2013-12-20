"""
Dummy module that simulates snimpy functionality on Keepalived 
for unit testing
"""

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
        self.virtualServerAddress = list()
        self.virtualServerPort = list()
        self.virtualServerRealServersTotal = list()


def load(mibname):
    """Dummy load method"""
    pass