"""
Director specific functionality
"""
import logging
import socket
import subprocess

# Local modules
from servers import Virtual, Real
import utils


logger = logging.getLogger('lvsm')

class Director(object):
    """
    Factory class that returns a director object based on the name provided
    """
    # directors = {'generic': GenericDirector,
    #              'ldirectord': Ldirectord,
    #              'keepalived': Keepalived}

    def __new__(self, name, ipvsadm, configfile='', restart_cmd='', nodes='', args=dict()):
        if name == 'keepalived':
            from modules.keepalived import Keepalived
            return Keepalived(ipvsadm, configfile, restart_cmd, nodes, args)
        elif name == 'ldirectord':
            from modules.ldirectord import Ldirectord
            return Ldirectord(ipvsadm, configfile, restart_cmd, nodes, args)
        else:
            # from genericdirector import GenericDirector
            return GenericDirector(ipvsadm, configfile, restart_cmd, nodes, args)

def get_ipvs():
    """Get the virtual server table that's stored in Kernel memory"""
    logger.debug('Building IPVS table.')
    # Location of the ip_vs table in the /proc fs
    proc_net_ipvs = "/proc/net/ip_vs"

    # Note: here we don't catch the exception
    # If /proc/net/ip_vs is not there or accessible, an exception should be raised
    ipvs_file = open(proc_net_ipvs)
    output = ipvs_file.read()
    ipvs_file.close()

    # Clear out the old virtual table
    virtuals = list()

    # Break up the output and generate VIP and RIPs from it
    # Assumption is that the first 3 lines of the ipvsadm output
    # are just informational so we skip them
    for line in output.split('\n')[3:]:
        if (line.startswith('TCP') or
            line.startswith('UDP') or
            line.startswith('FWM')):

            # break the virtual server line into tokens. There should only be 3
            tokens = line.split()
            # first one is the protocol
            proto = tokens[0]
            if line.startswith('FWM'):
                # there's no port number in fwm mode
                ip = tokens[1]
                port = ''
            else:    
                # second token will be ip:port
                ip, sep, port = tokens[1].rpartition(':')
            # 3rd is the scheduler
            sched = tokens[2]
            # [optional] 5th is the persistence timeout
            if len(tokens) == 5:
                persistence = tokens[4]
            else:
                persistence = None

            v = Virtual(proto, socket.inet_ntoa(ip), int(port, 16), sched, persistence)
            virtuals.append(v)
        # If the line doesn't begin with the above values, it's a realserver
        else:
            # The reals are always added to the last vip
            # This if prevents an error of adding RS to a non-existent VS
            if len(virtuals) > 0:
                tokens = line.split()
                if len(tokens) == 6:
                    ip, sep, port = tokens[1].rpartition(':')
                    method = tokens[2]
                    weight = tokens[3]
                    active = tokens[4]
                    inactive = tokens[5]
                    r = Real(socket.inet_ntoa(ip), int(port, 16), weight, method, active, inactive)
                    virtuals[-1].realServers.append(r)

    return virtuals

class GenericDirector(object):
    """
    Generic class that knows about ipvsadm. If director isn't defined, this
    is the fallback. Should be inherited by classes implementing specific
    director funcationality.
    """
    def __init__(self, ipvsadm, configfile='', restart_cmd='', nodes='', args=dict()):
        self.ipvsadm = ipvsadm
        self.configfile = configfile
        self.restart_cmd = restart_cmd
        if nodes != '':
            self.nodes = nodes.replace(' ', '').split(',')
        else:
            self.nodes = None
        self.hostname = socket.gethostname()
        # this variable will hold the full IPVS table
        self.virtuals = list()

    def disable(self, host, port='', reason=''):
        """
        Disable a previously Enabled server.
        To be implemented by inheriting classes
        """
        logger.error("Disable not implemented for 'generic' director")
        return False

    def enable(self, host, port=''):
        """
        Enable a previously disabled server.
        To be implemented by inheriting classes
        """
        logger.error("enable not implemented for 'generic' director")
        return False

    def show(self, numeric, color):
        # Call ipvsadm and do the color highlighting.
        result = ["", "Layer 4 Load balancing"]
        result += ["======================"]
        result += self.show_running(numeric, color)

        # Show a list of disabled real servers.
        disabled = self.show_real_disabled('', '', numeric)
        if disabled:
            header = ["", "Disabled real servers:", "----------------------"]
            disabled = header + disabled

        return result + disabled + ['']

    def show_running(self, numeric, color):
        """
        Show the running status of IPVS. Basically runs "ipvsadm".
        """
        # Create the IPVS table in memory
        self.virtuals = get_ipvs()
        result = list()
        for v in self.virtuals:
            result += v.__str__(numeric, color).split('\n')

        return result

    def show_virtual(self, host, port, proto, numeric, color):
        """Show status of virtual server.
        """
        # make sure we have a valid host
        hostips = utils.gethostbyname_ex(host)
        if not hostips:
            return list()

        # make sure the port is valid
        if port:
            portnum = utils.getportnum(port)
            if portnum == -1:
                return list()

        # Update the ipvs table
        self.virtuals = get_ipvs()

        result = ["", "Layer 4 Load balancing"]
        result += ["======================"]
        for v in self.virtuals:
            if v.proto == proto.upper() and v.ip in hostips:
                if not port or v.port == str(portnum):
                    result += v.__str__(numeric, color).split('\n')

        return result

    def show_real(self, host, port, numeric, color):
        """Show status of a real server across multiple VIPs.
        Will consider both active and disabled servers.
        """
        header = ["", "Layer 4 Load balancing" , "======================"]
        output = header

        active = self.show_real_active(host, port, numeric, color)
        if active:
            active = ["", "Active servers:", "---------------"] + active
            output = output + active

        disabled = self.show_real_disabled(host, port, numeric)
        if disabled:
            disabled = ["", "Disabled servers:", "-----------------"] + disabled
            output = output + disabled

        # return header + active + disabled + ["\n"]
        return output

    def show_real_active(self, host, port, numeric, color):
        """Show status of an active real server across multiple VIPs.
        """
        # make sure we have a valid host
        hostips = utils.gethostbyname_ex(host)

        if not hostips:
            return list()

        # If more than one ip is returned for a host. Use the first one
        hostip = hostips[0]
        # If port is defined verify that it's a valid number
        if port:
            portnum = utils.getportnum(port)
            if portnum == -1:
                return list()
        else:
            portnum = None

        # Update the ipvs table
        self.virtuals = get_ipvs()

        result = list()

        for v in self.virtuals:
            # for real in v.realServers: 
                # if real.ip == hostip:
                #     logger.debug("real port type: %s" % type(real.port))
                #     logger.debug("port num type: %s" % type(portnum))
                #     if not port or real.port == portnum:
                #         result += v.__str__(numeric, color, real.ip, port).split('\n')
            # result += v.__str__(numeric, color, hostip, portnum).split('\n')
            r = v.__str__(numeric, color, hostip, portnum)
            if r:
                result += r.split('\n')
        return result

    def show_real_disabled(self, host, port, numeric):
        """
        Show status of disabled real server across multiple VIPs.
        To be implemented by inheriting classes. 
        Return value must be a list
        """
        return list()

    def convert_filename(self, filename):
        """
        Convert a filename of format host[:port] to IP[:port]
        Assumption is that for hosts with more than one IP,
        the first IP in the list is used.
        """
        values = filename.split(':')
        portnum = -1
        if not values:
            return ''
        hostips = utils.gethostbyname_ex(values[0])
        if len(values) == 2:
            portnum = utils.getportnum(values[1])
        if portnum > -1:
            return hostips[0] + ':' + str(portnum)
        else:
            return hostips[0]

    def check_real(self, host, port):
        """Check a host/port to see if it's in the realserver list."""
        # useful with show_real command
        pass

    def restart(self):
        """Restart the director."""
        if self.restart_cmd:
            print "restaring director"
            try:
                result = subprocess.call(self.restart_cmd, shell=True)
            except OSError as e:
                print "[ERROR] problem restaring director - " + e.strerror
        else:
            print "[ERROR] 'director_cmd' not defined in config!"

    def parse_config(self, configfile):
        """Parse config file, and syntax check. 
        Returns True on success, False on failure.
        To be implemented by inheriting classes.
        """
        return True

    def get_virtual(self, protocol):
        """return a list of the virtual servers by protocol. 
        Used for autocomplete mode in the shell.
        """
        args = [self.ipvsadm, '-L']
        result = list()
        try:
            output = utils.check_output(args, silent=True)
        except OSError as e:
            logger.error(" %s" % e.strerror)
            return result
        lines = output.splitlines()
        for line in lines:
            if line.startswith(protocol.upper()):
                r, sep, temp = line.partition(':')
                result.append(r[5:])

        return result

    def get_real(self, protocol):
        """return a list of all real servers.
        Used for autocomplete mode in the shell."""

        args = [self.ipvsadm, '-L']
        result = list()
        prot = ''
        try:
            output = utils.check_output(args, silent=True)
        except OSError as e:
            logger.error(" %s" % e.strerror)
            return result

        lines = output.splitlines()

        for line in lines[3:]:
            if line[0:3] in ['TCP', 'UDP', 'FWM']:
                prot = line[0:3]
            elif (line.startswith("  ->") 
                  and (not protocol or protocol.upper() == prot)):
                r, sep , temp = line.partition(':')
                real = r[5:]
                if real not in result:
                    result.append(real)
        return result

    def filesync_nodes(self, op, filename):
        """
        Sync a file between nodes in the cluster. 
        op has to be one of 'remove' or 'copy'.
        filename is the name of the file to be copied/removed
        The method return True/False
        """
        if self.nodes is not None:
            for node in self.nodes:
                if node != self.hostname:

                    # Assumption is we only need to remotely remove a file
                    # Or copy a file to a remote location
                    if op == 'remove':
                        args = ['ssh', node, 'rm', filename]
                    elif op == 'copy':
                        remote = node + ":" + filename
                        args = ['scp', filename, remote]
                    else:
                        logger.error('Unknown operation \'%s\' in filesync method!' % op)
                        return False

                    logger.debug('Running command : %s' % (' '.join(args)))
                    try:
                        utils.check_output(args)
                    except OSError as e:
                        logger.error("Unable to sync state file to %s" % node)
                        logger.error(e)
                        return False
                    except subprocess.CalledProcessError as e:
                        logger.error("Unable to sync state file to %s" % node)
                        logger.error(e)
                        return False
        return True
