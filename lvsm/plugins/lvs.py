"""
Director specific funcationality
"""
from genericdirector import GenericDirector
from ldirectord import Ldirectord
from keepalived import Keepalived


class Director(object):
    """
    Factory class that returns a director object based on the name provided
    """
    directors = {'generic': GenericDirector,
                 'ldirectord': Ldirectord,
                 'keepalived': Keepalived}

    def __new__(self, name, maintenance_dir, ipvsadm,
                configfile='', restart_cmd='', nodes=''):
        if name != 'ldirectord' and name != 'keepalived':
            name = 'generic'
        return Director.directors[name](maintenance_dir, ipvsadm,
                                        configfile, restart_cmd, nodes)