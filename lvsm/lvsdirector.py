"""Director specific funcationality"""
import os
import socket
import subprocess
import sys
import time
import utils
import termcolor


class Server():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class Virtual(Server):
    def __init__(self, ip, port):
        Server.__init__(ip, port)
        self.realServers = list()


class GenericDirector(object):
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
        try:
            self.hostname = utils.check_output(['hostname', '-s']).rstrip()
        except (OSError, subprocess.CalledProcessError):
            self.hostname = ''

    def disable(self, host, port='', reason=''):
        """disable a previously disabled server.
        To be implemented by inheriting classes"""
        return False

    def enable(self, host, port=''):
        """enable a previously disabled server.
        To be implemented by inheriting classes"""
        return False

    def show(self, numeric, color):
        args = [self.ipvsadm, '-L']
        if numeric:
            args.append('-n')

        try:
            output = utils.check_output(args)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return
        except subprocess.CalledProcessError as e:
            print "[ERROR] problem with ipvsadm - " + e.output
            return

        if color:
            result = list()
            for line in output.split('\n'):
                if line.startswith('TCP') or line.startswith('UDP') or line.startswith('FWM'):
                    result.append(termcolor.colored(line, attrs=['bold']))
                else:
                    result.append(line)
        else:
            result = output.split('\n')

        # show a list of disabled real servers
        disabled = self.show_real_disabled('', '', numeric )
        if disabled:
            disabled = ["", "Disabled servers:", "-----------------"] + disabled

        return result + disabled

    def show_virtual(self, host, port, prot, numeric, color):
        """show status of virtual server"""
        protocols = {'tcp': '-t', 'udp': '-u', 'fwm': '-f'}
        protocol = protocols[prot]
        # make sure we have a valid host
        hostip = utils.gethostname(host)
        if not hostip:
            return
        # make sure the port is valid
        portnum = utils.getportnum(port)
        if portnum == -1:
            return
        args = [self.ipvsadm, '-L']
        if numeric:
            args.append('-n')

        args.append(protocol)
        args.append(hostip + ':' + str(portnum))
        try:
            output = utils.check_output(args)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return
        except subprocess.CalledProcessError as e:
            print "[ERROR] problem with ipvsadm - " + e.output
            return

        if color:
            result = list()
            for line in output.split('\n'):
                if line.startswith('TCP') or line.startswith('UDP') or line.startswith('FWM'):
                    result.append(termcolor.colored(line, attrs=['bold']))
                else:
                    result.append(line)
        else:
            result = output.split('\n')

        return result

    def show_real(self, host, port, numeric, color):
        """show status of real server across multiple VIPs"""
        active = self.show_real_active(host, port, numeric, color)
        if active:
            active = ["", "Active servers:", "---------------"] + active
        disabled = self.show_real_disabled(host, port, numeric)
        if disabled:
            disabled = ["", "Disabled servers:", "-----------------"] + disabled
        return active + disabled

    def show_real_active(self, host, port, numeric, color):
        """show status of active real server across multiple VIPs"""
        hostip = utils.gethostname(host)
        if not hostip:
            return
        portnum = utils.getportnum(port)
        if portnum == -1:
            return
        hostport = hostip + ":" + str(portnum)
        args = [self.ipvsadm, '-L', '-n']
        try:
            lines = utils.check_output(args)
        except OSError as e:
            print "[ERROR] " + e.strerror
            return
        except subprocess.CalledProcessError as e:
            print "[ERROR] problem with ipvsadm - " + e.output
            return

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
                    vipportname = socket.getservbyport(int(vipport))
                    v = virtual.split()[0] + ' ' + vipname + ':' + vipportname

                    rip = line.split()[1].split(":")[0]
                    (ripname, aliaslist, iplist) = socket.gethostbyaddr(rip)
                    ripport = line.split()[1].split(":")[1]
                    ripportname = socket.getservbyport(int(ripport))
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
        """stub funtion. To be implemented by inheriting classes"""
        pass

    def convert_filename(self, filename):
        """convert a filename of format host[:port] to IP[:port]"""
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
        """Check a host/port to see if it's in the realserver list"""
        # useful with show_real command
        pass

    def restart(self):
        """Restart the director"""
        if self.restart_cmd:
            print "restaring director"
            try:
                result = subprocess.call(self.restart_cmd, shell=True)
            except OSError as e:
                print "[ERROR] problem restaring director - " + e.strerror
        else:
            print "[ERROR] 'director_cmd' not defined in config!"


class Ldirectord(GenericDirector):
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        super(Ldirectord, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd, nodes)

    def disable(self, host, port='', reason=''):
        if self.maintenance_dir:
            hostip = utils.gethostname(host)
            if not hostip:
                return False
            if port:
                # check that it's a valid port
                portnum = utils.getportnum(port)
                if portnum == -1:
                    return False
                hostport = hostip + ":" + str(portnum)
            else:
                hostport = hostip
            # go through maint_dir to see if host is already disabled
            filenames = os.listdir(self.maintenance_dir)
            for filename in filenames:
                f = self.convert_filename(filename)
                if hostport == f or hostip == f:
                    print "host is already disabled!"
                    return True
            try:
                f = open(self.maintenance_dir + "/" + hostport, 'w')
                f.write(reason)
            except IOError as e:
                print "[ERROR] " + e.strerror + ": '" + e.filename +\
                      "'"
                return False

            if self.nodes is not None:
                filename = self.maintenance_dir + "/" + hostport
                for node in self.nodes:
                    if node != self.hostname:
                        remote = node + ":" + self.maintenance_dir
                        args = ['scp', filename, remote]
                        try:
                            output = utils.check_output(args)
                        except OSError as e:
                            print "[ERROR] problem disabling on remote node - " + e.strerror
                        except subprocess.CalledProcessError as e:
                            print "[ERROR] problem disabling on remote node - " + e.output
            # now confirm that it's removed from ldirector
            i = 0
            print "Disabling server ",
            while i < 3:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(1.5)
                i = i + 1
            output = self.show(numeric=True, color=False)
            for line in output:
                if hostport in line:
                    print " Failed"
                    # note: even if the real is still showing up, we've created
                    # the file, so we should still return true
                    return True
            print " OK"
            return True
        else:
            print "[ERROR] maintenance_dir not defined in config."
            return False

    def enable(self, host, port=''):
        """enable a previously disabled server"""
        hostip = utils.gethostname(host)
        if not hostip:
            return False
        if port:
            # check that it's a valid port
            portnum = utils.getportnum(port)
            if portnum == -1:
                return False
            hostport = hostip + ":" + str(portnum)
        else:
            hostport = hostip
        if self.maintenance_dir:
            filenames = os.listdir(self.maintenance_dir)
            for filename in filenames:
                f = self.convert_filename(filename)
                if hostport == f or hostip == f or hostip + ":" in f:
                    try:
                        os.unlink(self.maintenance_dir + "/" + filename)
                    except OSError as e:
                        print "[ERROR] " + e.strerror + ": '" +\
                              e.filename + "'"
                        return False

                    if self.nodes is not None:
                        for node in self.nodes:
                            if node != self.hostname:
                                cmd = "rm " + self.maintenance_dir + "/" + filename
                                args = ['ssh', node, cmd]
                                try:
                                    output = utils.check_output(args)
                                except OSError as e:
                                    print "[ERROR] problem enabling on remote node - " + e.strerror
                                except subprocess.CalledProcessError as e:
                                    print "[ERROR] problem enabling on remote node - " + e.output
                    i = 0
                    print "Enabling server ",
                    while i < 3:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        time.sleep(1.5)
                        i = i + 1

                    # verify that the host is active in ldirectord
                    output = self.show(numeric=True, color=False)
                    for line in output:
                        if hostport in line:
                            print " OK"
                            return True
                    # if we get to this point, means the host is not active
                    print " Failed"
                    # note: even if the real is not showing up, we have remove
                    # the file, so we should still return true
                    return True
        else:
            print "[ERROR] maintenance_dir not defined!"
            return False

    def show_real_disabled(self, host, port, numeric):
        """show status of disabled real server across multiple VIPs"""
        # note that host='' and port='' returns all disabled server
        if host and port:
            hostip = utils.gethostname(host)
            if not hostip:
                return
            portnum = utils.getportnum(port)
            if portnum == -1:
                return
            hostport = hostip + ":" + str(portnum)
        # output = ["", "Disabled servers:", "-----------------"]
        output = list()
        filenames = os.listdir(self.maintenance_dir)
        for filename in filenames:
            try:
                f = open(self.maintenance_dir + "/" + filename)
                reason = 'Reason: ' + f.readline()
            except IOError as e:
                reason = ''
                print "[ERROR] " + e.strerror + ' \'' + e.filename + '\''
            if ((not host and not port) or
                self.convert_filename(filename) == hostip or
                self.convert_filename(filename) == hostip + ":" +
                str(portnum)):
                # decide if we have to convert to hostname or not
                if numeric:
                    output.append(filename + "\t\t" + reason)
                else:
                    rip = filename.split(":")[0]
                    try:
                        (ripname, al, ipl) = socket.gethostbyaddr(rip)
                    except socket.herror, e:
                        print "[ERROR] " + str(e)
                        return False
                    if len(filename.split(":")) == 2:
                        ripport = filename.split(":")[1]
                        ripportname = socket.getservbyport(int(ripport))
                        ripname = ripname + ':' + ripportname
                    else:
                        pass
                    output.append(ripname + "\t\t" + reason)
        return output


class Keepalived(GenericDirector):
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        super(Keepalived, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd)


class Director(object):
    """Factory class to return the right kind of director"""
    directors = {'generic': GenericDirector,
                 'ldirectord': Ldirectord,
                 'keepalived': Keepalived}

    def __new__(self, name, maintenance_dir, ipvsadm,
                configfile='', restart_cmd='', nodes=''):
        if name != 'ldirectord' and name != 'keepalived':
            name = 'generic'
        return Director.directors[name](maintenance_dir, ipvsadm,
                                        configfile, restart_cmd, nodes)
