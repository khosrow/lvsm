import logging
import sys
from lvsm import genericdirector, utils

logger = logging.getLogger('lvsm')

# needed for testing the code on non-Linux platforms
try:
    from snimpy import manager
    from snimpy import mib
    from snimpy import snmp
except ImportError:
    logger.error("Python module 'snimpy' not found,loading a dummy module.")
    logger.error("'enable' and 'disable' commands will not be availble.""")
    from lvsm.snimpy_dummy import manager
    from lvsm.snimpy_dummy import mib
    from lvsm.snimpy_dummy import snmp
    
class Keepalived(genericdirector.GenericDirector):
    """
    Implements Keepalived specific functions. Stub for now.
    """
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        super(Keepalived, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd)

    def disable(self, host, port='', reason=''):
        """
        Disable a real server in keepalived. This command rellies on snimpy
        and will set the weight of the real server to 0.
        The reason is not used in this case.
        """
        logger.debug("host: %s" % host)
        logger.debug("port: %s" % port)
        manager.load('KEEPALIVED-MIB')
        m = manager.Manager('localhost', 'private')

        hostip = utils.gethostname(host)
        if not hostip:
            return False
        if port:
            # check that it's a valid port
            portnum = utils.getportnum(port)
            if portnum == -1:
                return False
          
        for idx in m.realServerTable:
            # should verify address family here
            # if self.snmp.realServerTable[idx].realServerAddress == ""

            # The address here will be a hex number
            hexip = m.realServerTable[idx].realServerAddress
            realip = utils.hextoip(hexip)
            realport = int(m.realServerTable[idx].realServerPort,16)

            if realip == hostip:
                if not port or portnum == realport:
                    # If port is not defined, disable the server at all ports
                    try:
                        m.realServerTable[idx].realServerWeight = 0
                    except snmp.SNMPException as e:
                        logger.errro(e)
                        return False

        return True

    def enable(self, host, port=''):
        """
        Enable a real server in keepalived. This command rellies on snimpy
        and will set the weight of the real server to 0.
        The reason is not used in this case.
        """
        logger.debug("host: %s" % host)
        logger.debug("port: %s" % port)

        manager.load('KEEPALIVED-MIB')
        m = manager.Manager('localhost', 'private')

        hostip = utils.gethostname(host)
        if not hostip:
            return False
        if port:
            # check that it's a valid port
            portnum = utils.getportnum(port)
            if portnum == -1:
                return False
          
        for idx in m.realServerTable:
            # should verify address family here
            # if self.snmp.realServerTable[idx].realServerAddress == ""

            # The address here will be a hex number
            hexip = m.realServerTable[idx].realServerAddress
            realip = utils.hextoip(hexip)
            realport = int(m.realServerTable[idx].realServerPort,16)

            if realip == hostip:
                if not port or portnum == realport:
                    # If port is not defined, disable the server at all ports
                    try:
                        m.realServerTable[idx].realServerWeight = 1
                    except snmp.SNMPException as e:
                        logger.errro(e)
                        return False

        return True
