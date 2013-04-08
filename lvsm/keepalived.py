from genericdirector import GenericDirector

class Keepalived(GenericDirector):
    """
    Implements Keepalived specific functions. Stub for now.
    """
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        super(Keepalived, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd)
