"""
Director specific funcationality
"""
from genericdirector import GenericDirector
from modules.ldirectord import Ldirectord
from modules.keepalived import Keepalived

class Director(object):
    """
    Factory class that returns a director object based on the name provided
    """
    directors = {'generic': GenericDirector,
                 'ldirectord': Ldirectord,
                 'keepalived': Keepalived}

    def __new__(self, name, ipvsadm, configfile='', restart_cmd='', nodes=''):
        if name == 'keepalived':
            from modules.keepalived import Keepalived
            return Keepalived(ipvsadm, configfile, restart_cmd, nodes)
        elif name == 'ldirectord':
            from modules.ldirectord import Ldirectord
            return Ldirectord(ipvsadm, configfile, restart_cmd, nodes)
        else:
            from genericdirector import GenericDirector
            return GenericDirector(ipvsadm, configfile, restart_cmd, nodes)
