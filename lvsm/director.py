"""Director specific funcationality"""
import os
import subprocess


class Director():
    def __init__(self, name='', maintenance_dir=''):
        self.maintenance_dir = maintenance_dir
        self.name = name

    def disable(self, host):
        if self.name == 'ldirectord':
            if self.maintenance_dir:
                try:
                    f = open(self.maintenance_dir + host, 'w')
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

    def enable(self, host):
        if self.name == 'ldirectord':
            if self.maintenance_dir:
                try:
                    os.unlink(self.maintenance_dir + host)
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
            print "[ERROR] port number must be an integer!"
            return 1
        args = [self.config['ipvsadm'], '--list']
        p = subprocess.Popen(args, stdout=subprocess.PIPE())
        stdout, stderr = p.communicate()
        lines = stdout.split('\n')
        virtual = ""
        real = ""
        for line in lines:
            if (line.startswith("TCP") or
                line.startswith("UDP") or
                line.startswith("FWM")) :
                virtual = lin
            hostservice = host + ":" + port
            if line.find(hostservice):
                print virtual
                print line
