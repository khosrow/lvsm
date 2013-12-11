"""
Dummy module that simulates snimpy functionality on Keepalived 
for test systems
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
        pass

    def realServerAddress(self):
        pass


def load(mibname):
    print "loading %s" % mibname