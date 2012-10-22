"""Director specific funcationality"""
import os
import socket
import subprocess

import utils
import sys


class Director():
    def __init__(self, name, maintenance_dir, ipvsadm):
        self.maintenance_dir = maintenance_dir
        self.name = name
        self.ipvsadm = ipvsadm

    def show(self, numeric):
        args = self.ipvsadm + ' -L '
        if numeric:
            args = args + ' -n'
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            print stdout
        elif stderr:
            print stderr
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
            print ("[ERROR] no valid director defined, " +
                   " don't know how to disable servers!")
            return False

    def enable(self, host, port=''):
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
                try:
                    os.unlink(self.maintenance_dir + "/" + hostport)
                except OSError as e:
                    print "[ERROR] " + e.strerror + ": '" + e.filename +\
                          "'"
                    return False
                return True
            else:
                print "[ERROR] maintenance_dir not defined in config."
                return False
        else:
            print ("[ERROR] no valid director defined!" +
                   " don't know how to enable servers!")
            return False

    def show_virtual(self, host, port, prot, numeric):
        """show status of virtual server"""
        protocols = {'tcp': '-t', 'udp': '-u', 'fwm': '-f'}
        protocol = protocols[prot]
        hostip = utils.gethostname(host)
        if not hostip:
            return False
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
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with ipvsadm - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            print stdout
        elif stderr:
            print stderr
        return True

    def show_real(self, host, port, numeric):
        """show status of real server across multiple VIPs"""
        hostip = utils.gethostname(host)
        if not hostip:
            return False
        portnum = utils.getportnum(port)
        if portnum == -1:
            return False
        args = self.ipvsadm + ' -Ln'
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
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
            hostservice = hostip + ":" + str(portnum)
            if line.find(hostservice) != -1:
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
                # assumption is filename will be HOSTIP[:PORT]
                # but we need to handle the case if someone makes the
                # file from CLI and is of format HOSTNAME[:PORT]
                try:
                    f = open(self.maintenance_dir + "/" + filename)
                    reason = 'Reason: ' + f.readline()
                except IOError as e:
                    reason = ''
                    print "[ERROR] " + e.strerror + ' \'' + e.filename + '\''
                if (filename == hostip or
                    filename == hostip + ":" + str(portnum)):
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

    def check_real(self, host, port):
        """Check a host/port to see if it's in the realserver list"""
        # useful with show_real command
        pass
