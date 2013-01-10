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


class Director():
    def __init__(self, name, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd=''):
        self.maintenance_dir = maintenance_dir
        self.name = name
        self.ipvsadm = ipvsadm
        self.configfile = configfile
        self.restart_cmd = restart_cmd

    def show(self, numeric):
        args = self.ipvsadm + ' -L '
        if numeric:
            args = args + ' -n'
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            print stdout
        elif stderr:
            print stderr
            return False
        return True

    def disable(self, host, port='', reason=''):
        # check that it's a valid port
        if port:
            portnum = utils.getportnum(port)
            if portnum == -1:
                return False
        if self.name == 'ldirectord':
            if self.maintenance_dir:
                hostip = utils.gethostname(host)
                if not hostip:
                    return False
                if port:
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
        else:
            print "[ERROR] no valid director defined, " +\
                  " don't know how to disable servers!"
            return False

    def enable(self, host, port=''):
        """enable a previously disabled server"""
        # check that it's a valid port
        if port:
            portnum = utils.getportnum(port)
            if portnum == -1:
                return False
        hostip = utils.gethostname(host)
        if not hostip:
            return False
        if self.name == 'ldirectord':
            if port:
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
        else:
            print ("[ERROR] no valid director defined!" +
                   " don't know how to enable servers!")
            return False

    def show_virtual(self, host, port, prot, numeric):
        """show status of virtual server"""
        protocols = {'tcp': '-t', 'udp': '-u', 'fwm': '-f'}
        protocol = protocols[prot]
        # make sure we have a valid host
        hostip = utils.gethostname(host)
        if not hostip:
            return False
        # make sure the port is valid
        portnum = utils.getportnum(port)
        if portnum == -1:
            return False
        if numeric:
            display_flag = '-n'
        else:
            display_flag = ''
        args = (self.ipvsadm + ' -L ' + display_flag + ' ' + protocol + ' ' +
                hostip + ':' + str(portnum))
        # utils.execute(args, "problem with ipvsadm", pipe=True)
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            print stdout
        elif stderr:
            # capture the useless ipvs error message and return proper error
            if stderr.rstrip() == "Memory allocation problem":
                print "Virtual service not defined!"
            else:
                print stderr
            return False
        return True

    def show_real(self, host, port, numeric):
        """show status of real server across multiple VIPs"""
        hostip = utils.gethostname(host)
        if not hostip:
            return False
        portnum = utils.getportnum(port)
        if portnum == -1:
            return False
        hostport = hostip + ":" + str(portnum)
        args = self.ipvsadm + ' -Ln'
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            lines = stdout.split('\n')
        else:
            lines = ""
        virtual = ""
        real = ""
        output = list()
        # find the output line that contains the rip
        for line in lines:
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
        if output:
            print ""
            print "Active servers:"
            print "---------------"
        for line in output:
            print line
        # now check to see if any servers are disabled
        if self.name == 'ldirectord':
            output = list()
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
            if output:
                print ""
                print "Disabled servers:"
                print "-----------------"
            for line in output:
                print line
        print ""
        return True

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
