"""Director specific funcationality"""
import os
import socket
import subprocess
import lvsm


class Director():
    def __init__(self, name, maintenance_dir, ipvsadm):
        self.maintenance_dir = maintenance_dir
        self.name = name
        self.ipvsadm = ipvsadm

    def disable(self, host, port=''):
        # check that it's a valid port
        if port:
            try:
                int(port)
            except ValueError as e:
                try:
                    portnum = socket.getservbyname(port)
                except IOError as e:
                    print "[ERROR] " + str(e)
                    return 1
        if self.name == 'ldirectord':
            if self.maintenance_dir:
                if port:
                    hostport = host + ":" + port
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
            try:
                int(port)
            except ValueError as e:
                try:
                    portnum = socket.getservbyname(port)
                except IOError as e:
                    print "[ERROR] " + str(e)
                    return
        if self.name == 'ldirectord':
            if port:
                hostport = host + ":" + port
            else:
                hostport = host
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

    def show_real(self, host, port):
        """show status of real server across multiple VIPs"""
        try:
            portnum = int(port)
        except ValueError as e:
            portname = port
        else:
            portname = socket.getservbyport(portnum)
        args = [self.ipvsadm, '--list']
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
            hostservice = host + ":" + portname
            if line.find(hostservice) != -1:
                output.append(virtual)
                output.append(line)
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
                if filename == host or filename == host + ":" + portname:
                    output.append(filename)
            if output:
                print ""
                print "Disabled servers:"
                print "-----------------"
            for line in output:
                print line
        print ""

    def check_real(self, host, port):
        """Check a host/port to see if it's in the realserver list"""
        pass
