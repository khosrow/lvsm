"""
Director specific funcationality
"""
import socket
import subprocess
import utils
import termcolor
import logging

logger = logging.getLogger('lvsm')

class Server():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class Virtual(Server):
    def __init__(self, proto, ip, port, sched, persistence=None):
        Server.__init__(self, ip, port)
        self.proto = proto
        self.realServers = list()
        self.sched = sched
        self.persistence = persistence

    def __str__(self, numeric=True, color=False, real=None, port=None):
        """provide an easy way to print this object"""
        proto = self.proto.upper().ljust(4)
        host = self.ip
        service = self.port

        logger.debug("proto: %s" % proto)
        logger.debug("host: %s" % host)
        logger.debug("service: %s" % service)

        if self.proto.upper() == 'FWM':
            pass
        elif not numeric:
            try:
                try:
                    host, aliaslist, addrlist = socket.gethostbyaddr(self.ip)
                except socket.herror:
                    pass
                service = socket.getservbyport(int(self.port))
            except socket.error:
                pass
        if self.proto.upper() == 'FWM':
            ipport = host.ljust(40)
        else:
            ipport = (host + ":" + service).ljust(40)

        sched = self.sched.ljust(7)

        if self.persistence:
            line = "%s %s %s persistence %s" % (proto, ipport, sched, self.persistence)
        else:
            line = "%s %s %s" % (proto, ipport, sched)

        if color:
            line = termcolor.colored(line, attrs=['bold'])

        output = [line]
        for r in self.realServers:
            if real:
                if r.ip == real:
                    if port:
                        if int(r.port) == port:
                            output = [line]
                            output.append(r.__str__(numeric,color))
                    else:
                        output = [line]
                        output.append(r.__str__(numeric,color))

            else:
                output.append(r.__str__(numeric, color))

        # If a real server is provided, don't return empty VIPs
        if real:
            if len(output) == 1:
                return ''

        # Add space between each VIP in the final output
        if output:
            output.append('')

        return '\n'.join(output)

        # # line = "IP: %s  Port: %s  Protocol: %s  Scheduler: %s" % (host, service, self.proto, self.sched)
        # header = "Protocol  IP:port                                  Scheduler  Flags"
        # hr = "--------  ---------------------------------------  ---------  --------"
        # proto = self.proto.upper().ljust(8)
        # ipport = (host + ":" + service).ljust(39)
        # line = "%s  %s  %s" % (proto, ipport, self.sched)
        # if color:
        #     line = termcolor.colored(line, attrs=['bold'])

        # output = [header, hr, line]
        # header = "Label     IP:port                                  Method   Weight  ActiveConn  InactiveConn"
        # hr = "--------  ---------------------------------------  -------  ------  ----------  ------------"
        # output.append('')
        # output.append(header)
        # output.append(hr)
        # for r in self.realServers:
        #     output.append(r.__str__(numeric,color))
        # output.append('')
        # output.append('')
        # return '\n'.join(output)


class Real(Server):
    def __init__(self, ip, port, weight, method, active, inactive):
        Server.__init__(self, ip,port)
        self.weight = weight
        self.method = method
        self.active = active
        self.inactive = inactive

    def __str__(self, numeric=False, color=False):
        host = self.ip
        service = self.port
        if not numeric:
            try:
                host, aliaslist, addrlist = socket.gethostbyaddr(self.ip)
            except socket.herror:
                pass
            try:
                service = socket.getservbyport(int(self.port))
            except socket.error:
                pass
        ipport = (host + ":" + service).ljust(40)
        method = self.method.ljust(7)
        weight = self.weight.ljust(6)
        active = self.active.ljust(10)
        inactive = self.inactive.ljust(10)
        line = "  -> %s %s %s %s %s" % (ipport, method, weight, active, inactive)
        # line = "          %s %s  %s  %s  %s" % (ipport, method, weight, active, inactive)
        # if real server weight is zero, we highlight it as red
        if color and self.weight == '0':
            line = termcolor.colored(line, 'red')
        return line


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

    def build_ipvs(self):
        """Build a model fo the running ipvsadm table internally"""
        args = [self.ipvsadm, '-L', '-n']

        try:
            output = utils.check_output(args)
        except OSError as e:
            logger.error("Problem with ipvsadm - %s" % e.strerror)
            return False
        except subprocess.CalledProcessErrror as e:
            logger.error("Problem with ipvsadm - %s" % e.output)
            return False

        # Clear out the old virtual table
        self.virtuals = list()
        # Break up the output and generate VIP and RIPs from it
        # Assumption is that the first 3 lines of the ipvsadm output
        # are just informational so we skip them
        for line in output.split('\n')[3:]:
            if (line.startswith('TCP') or
                line.startswith('UDP') or
                line.startswith('FWM')):

                # break the virtual line into tokens. There should only be 3
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

                v = Virtual(proto, ip, port, sched, persistence)
                self.virtuals.append(v)
            # If the line doesn't begin with the above values, it is realserver
            else:
                # The reals are always added to the last vip
                if len(self.virtuals) > 0:
                    tokens = line.split()
                    if len(tokens) == 6:
                        ip, sep, port = tokens[1].rpartition(':')
                        method = tokens[2]
                        weight = tokens[3]
                        active = tokens[4]
                        inactive = tokens[5]
                        v = self.virtuals[-1]
                        r = Real(ip, port, weight, method, active, inactive)
                        v.realServers.append(r)

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
        else:
            disabled = list()

        return result + disabled + ['']

    def show_running(self, numeric, color):
        """
        Show the running status of IPVS. Basically runs "ipvsadm".
        """
        # Create the IPVS table in memory
        self.build_ipvs()
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
        self.build_ipvs()

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
        self.build_ipvs()

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
        Sync a file between nodes in the cluste.
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
