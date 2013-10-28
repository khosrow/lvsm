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
    def __init__(self, ip, port):
        Server.__init__(ip, port)
        self.realServers = list()


class GenericDirector(object):
    """
    Generic class that knows about ipvsadm. If director isn't defined, this
    is the fallback. Should be inherited by classes implementing specific
    director funcationality.
    """
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        self.maintenance_dir = maintenance_dir
        self.ipvsadm = ipvsadm
        self.configfile = configfile
        self.restart_cmd = restart_cmd
        if nodes != '':
            self.nodes = nodes.replace(' ', '').split(',')
        else:
            self.nodes = None
        self.hostname = socket.gethostname()

    def disable(self, host, port='', reason=''):
        """
        Disable a previously Enabled server.
        To be implemented by inheriting classes
        """
        return False

    def enable(self, host, port=''):
        """
        Enable a previously disabled server.
        To be implemented by inheriting classes
        """
        return False

    def show(self, numeric, color):
        # Call ipvsadm and do the color highlighting.
        result = self.show_running(numeric, color)

        # Show a list of disabled real servers.
        disabled = self.show_real_disabled('', '', numeric)
        if disabled:
            header = ["", "Disabled servers:", "-----------------"]
            disabled = header + disabled

        return result + disabled

    def show_running(self, numeric, color):
        """
        Show the running status of IPVS. Basically runs "ipvsadm".
        """
        args = [self.ipvsadm, '-L']
        if numeric:
            args.append('-n')

        try:
            output = utils.check_output(args)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return list()
        except subprocess.CalledProcessError as e:
            print "[ERROR] problem with ipvsadm - " + e.output
            return list()

        if color:
            result = list()
            for line in output.split('\n'):
                if (line.startswith('TCP') or
                    line.startswith('UDP') or
                    line.startswith('FWM')):
                    result.append(termcolor.colored(line, attrs=['bold']))
                else:
                    result.append(line)
        else:
            result = output.split('\n')
        return result

    def show_virtual(self, host, port, prot, numeric, color):
        """Show status of virtual server.
        """
        protocols = {'tcp': '-t', 'udp': '-u', 'fwm': '-f'}
        protocol = protocols[prot]
        # make sure we have a valid host
        hostip = utils.gethostname(host)
        if not hostip:
            return list()
        # make sure the port is valid
        portnum = utils.getportnum(port)
        if portnum == -1:
            return list()
        args = [self.ipvsadm, '-L']
        if numeric:
            args.append('-n')

        args.append(protocol)
        args.append(hostip + ':' + str(portnum))
        try:
            output = utils.check_output(args)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return list()
        except subprocess.CalledProcessError as e:
            print "[ERROR] problem with ipvsadm - " + e.output
            return list()

        if color:
            result = list()
            for line in output.split('\n'):
                if (line.startswith('TCP') or
                    line.startswith('UDP') or
                    line.startswith('FWM')):
                    result.append(termcolor.colored(line, attrs=['bold']))
                else:
                    result.append(line)
        else:
            result = output.split('\n')

        return result

    def show_real(self, host, port, numeric, color):
        """Show status of a real server across multiple VIPs.
        Will consider both active and disabled servers.
        """
        active = self.show_real_active(host, port, numeric, color)
        if active:
            active = ["", "Active servers:", "---------------"] + active
        disabled = self.show_real_disabled(host, port, numeric)
        if disabled:
            header = ["", "Disabled servers:", "-----------------"]
            disabled = header + disabled
        return active + disabled

    def show_real_active(self, host, port, numeric, color):
        """Show status of an active real server across multiple VIPs.
        """
        hostip = utils.gethostname(host)
        if not hostip:
            return list()
        portnum = utils.getportnum(port)
        if portnum == -1:
            return list()
        hostport = hostip + ":" + str(portnum)
        args = [self.ipvsadm, '-L', '-n']
        try:
            lines = utils.check_output(args)
        except OSError as e:
            print "[ERROR] " + e.strerror
            return list()
        except subprocess.CalledProcessError as e:
            print "[ERROR] problem with ipvsadm - " + e.output
            return list()

        virtual = ""
        real = ""
        # output = ["", "Active servers:", "---------------"]
        output = list()
        # find the output line that contains the rip
        for line in lines.split('\n'):
            if (line.startswith("TCP") or
                line.startswith("UDP") or
                line.startswith("FWM")):
                virtual = line

            if hostport in line:
                if numeric:
                    v = '  '.join(virtual.split()[:2])
                    r = '  ' + ' '.join(line.split()[:2])
                else:
                    # convert host IP and port num to names before displaying
                    vip = virtual.split()[1].split(":")[0]
                    (vipname, aliaslist, iplist) = socket.gethostbyaddr(vip)
                    vipport = virtual.split()[1].split(":")[1]
                    try: 
                        vipportname = socket.getservbyport(int(vipport))
                    except socket.error as e:
                        vipportname = vipport
                    v = virtual.split()[0] + ' ' + vipname + ':' + vipportname

                    rip = line.split()[1].split(":")[0]
                    (ripname, aliaslist, iplist) = socket.gethostbyaddr(rip)
                    ripport = line.split()[1].split(":")[1]
                    try:
                        ripportname = socket.getservbyport(int(ripport))
                    except socket.error as e:
                        ripportname = ripportname

                    r = '  -> ' + ripname + ':' + ripportname

                # colorize output
                if color:
                    a = ['bold']
                else:
                    a = None

                output.append(termcolor.colored(v, attrs=a))
                output.append(r)

        return output

    def show_real_disabled(self, host, port, numeric):
        """Show status of disabled real server across multiple VIPs.
        To be implemented by inheriting classes. 
        Return value must be a list
        """
        return list()

    def convert_filename(self, filename):
        """Convert a filename of format host[:port] to IP[:port]"""
        values = filename.split(':')
        portnum = -1
        if not values:
            return ''
        hostip = utils.gethostname(values[0])
        if len(values) == 2:
            portnum = utils.getportnum(values[1])
        if portnum > -1:
            return hostip + ':' + str(portnum)
        else:
            return hostip

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
            output = utils.check_output(args)
        except OSError as e:
            logger.error(" %s" % e.strerror)
            return result

        for line in output.splitlines():
            if line.startswith(protocol):
                r, sep, temp = line.partition(':')
                result.append(r[5:])

        return result

    def get_real(self):
        """return a list of all real servers.
        Used for autocomplete mode in the shell."""
        return list()
