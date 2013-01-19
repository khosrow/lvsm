"""Director specific funcationality"""
import os
import socket
import subprocess
import sys
import utils


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
                 configfile='', restart_cmd=''):
        self.maintenance_dir = maintenance_dir
        self.ipvsadm = ipvsadm
        self.configfile = configfile
        self.restart_cmd = restart_cmd

    def disable(self, host, port='', reason=''):
        """disable a previously disabled server.
        To be implemented by inheriting classes"""
        return False

    def enable(self, host, port=''):
        """enable a previously disabled server.
        To be implemented by inheriting classes"""
        return False

    def show(self, numeric):
        args = [self.ipvsadm, '-L']        
        if numeric:
            args.append('-n')
        try:
            try:
                output = subprocess.check_output(args)
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return        
        return output.split('\n')

    def show_virtual(self, host, port, prot, numeric):
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
            try:
                output = subprocess.check_output(args)
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return     
        return output.split('\n')

    def show_real(self, host, port, numeric):
        """show status of real server across multiple VIPs"""
        active = self.show_real_active(host, port, numeric)
        if active is None:
            active = list()
        disabled = self.show_real_disabled(host, port, numeric)
        if disabled is None:
            disabled = list()
        return active + disabled

    def show_real_active(self, host, port, numeric):
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
            try:
                lines = subprocess.check_output(args)
            except AttributeError as e:
                lines, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            print "[ERROR] " + e.strerror
            return
        
        virtual = ""
        real = ""
        output = ["", "Active servers:", "---------------"]
        # find the output line that contains the rip
        for line in lines.split('\n'):
            if (line.startswith("TCP") or
                line.startswith("UDP") or
                line.startswith("FWM")):
                virtual = line
            if line.find(hostport) != -1:
                if numeric:
                    output.append('  '.join(virtual.split()[:2]))
                    output.append('  ' + ' '.join(line.split()[:2]))
                else:
                    # convert host IP and port num to names before displaying
                    vip = virtual.split()[1].split(":")[0]
                    (vipname, aliaslist, iplist) = socket.gethostbyaddr(vip)
                    vipport = virtual.split()[1].split(":")[1]
                    vipportname = socket.getservbyport(int(vipport))
                    rip = line.split()[1].split(":")[0]
                    (ripname, aliaslist, iplist) = socket.gethostbyaddr(rip)
                    ripport = line.split()[1].split(":")[1]
                    ripportname = socket.getservbyport(int(ripport))
                    output.append(virtual.split()[0] + ' ' + vipname + ':' +
                                  vipportname)
                    output.append('  -> ' + ripname + ':' + ripportname)
        output.append("")
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
                 configfile='', restart_cmd=''):
        super(Ldirectord, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd)

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
                if hostport == f or hostip == f:
                    try:
                        os.unlink(self.maintenance_dir + "/" + filename)
                    except OSError as e:
                        print "[ERROR] " + e.strerror + ": '" +\
                              e.filename + "'"
                        return False
                    return True
        else:
            print "[ERROR] maintenance_dir not defined!"
            return False

    def show_real_disabled(self, host, port, numeric):
        """show status of disabled real server across multiple VIPs"""
        hostip = utils.gethostname(host)
        if not hostip:
            return
        portnum = utils.getportnum(port)
        if portnum == -1:
            return
        hostport = hostip + ":" + str(portnum)
        output = ["", "Disabled servers:", "-----------------"]
        filenames = os.listdir(self.maintenance_dir)
        for filename in filenames:
            try:
                f = open(self.maintenance_dir + "/" + filename)
                reason = 'Reason: ' + f.readline()
            except IOError as e:
                reason = ''
                print "[ERROR] " + e.strerror + ' \'' + e.filename + '\''
            if (self.convert_filename(filename) == hostip or
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
                 configfile='', restart_cmd=''):
        super(Keepalived, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd)


class Director(object):
    """Factory class to return the right kind of director"""
    directors = {'generic': GenericDirector,
                 'ldirectord': Ldirectord,
                 'keepalived': Keepalived}

    def __new__(self, name, maintenance_dir, ipvsadm,
                configfile='', restart_cmd=''):
        if name != 'ldirectord' and name != 'keepalived':
            name = 'generic'
        return Director.directors[name](maintenance_dir, ipvsadm,
                                        configfile, restart_cmd)
