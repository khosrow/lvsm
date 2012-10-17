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

    def disable(self, host, port=''):
        # check that it's a valid port
        if port:
            portnum = utils.getportnum(port)
            if portnum == -1:
                return
        if self.name == 'ldirectord':
            if self.maintenance_dir:
                hostip = utils.gethostname(host)
                if not hostip:
                    return
                if port:
                    hostport = hostip + ":" + str(portnum)
                else:
                    hostport = host
                try:
                    f = open(self.maintenance_dir + "/" + hostport, 'w')
                    f.write("# created by LVSM")
                except IOError as e:
                    print "[ERROR] unable to disable " + host
                    print "[ERROR] " + e.strerror + ": '" + e.filename +\
                          "'"
            else:
                print ("[ERROR] maintenance_dir not defined in config." +
                       " Could not disable server!")
        else:
            print ("[ERROR] no valid director defined." +
                   " Don't know how to disable servers!")

    def enable(self, host, port=''):
        # check that it's a valid port
        if port:
            portnum = utils.getportnum(port)
            if portnum == -1:
                return
        hostip = utils.gethostname(host)
        if not hostip:
            return
        if self.name == 'ldirectord':
            if port:
                hostport = hostip + ":" + str(portnum)
            else:
                hostport = hostip
            if self.maintenance_dir:
                try:
                    os.unlink(self.maintenance_dir + "/" + hostport)
                except OSError as e:
                    print "[ERROR] could not enable " + host
                    print "[ERROR] " + e.strerror + ": '" + e.filename +\
                          "'"
            else:
                print ("[ERROR] maintenance_dir not defined in config." +
                       " Could not enable real servers!")
        else:
            print ("[ERROR] no valid director defined." +
                   " Don't know how to disable servers!")

    def show_virtual(self, host, port, prot, numeric):
        """show status of virtual server"""
        protocols = {'tcp': '-t', 'udp': '-u', 'fwm': '-f'}
        protocol = protocols[prot]
        hostip = utils.gethostname(host)
        if not hostip:
            return
        portnum = utils.getportnum(port)
        if portnum == -1:
            return
        if numeric:
            display_flag = '-n'
        else:
            display_flag = ''
        args = (self.ipvsadm + ' -L ' + display_flag + ' ' + protocol + ' ' +
                hostip + ':' + str(portnum))
        utils.execute(args, "problem with ipvsadm", pipe=True)

    def show_real(self, host, port, numeric):
        """show status of real server across multiple VIPs"""
        hostip = utils.gethostname(host)
        if not hostip:
            return
        portnum = utils.getportnum(port)
        if portnum == -1:
            return
        args = self.ipvsadm + ' -Ln'
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = proc.communicate()
        if stdout:
            lines = stdout.split('\n')
        else:
            lines = ""
        virtual = ""
        real = ""
        output = list()
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
                if (filename == hostip or
                    filename == hostip + ":" + str(portnum)):
                    if numeric:
                        output.append(filename)
                    else:
                        rip = filename.split(":")[0]
                        try:
                            (ripname, aliaslist, iplist) = socket.gethostbyaddr(rip)
                        except socket.herror, e:
                            print >> sys.stderr, str(e)
                            return
                        if len(filename.split(":")) == 2:
                            ripport = filename.split(":")[1]
                            ripportname = socket.getservbyport(int(ripport))
                            ripname = ripname + ':' + ripportname
                        else:
                            pass
                        output.append(ripname)
            if output:
                print ""
                print "Disabled servers:"
                print "-----------------"
            for line in output:
                print line
        print ""

    def check_real(self, host, port):
        """Check a host/port to see if it's in the realserver list"""
        # useful with show_real command
        pass
