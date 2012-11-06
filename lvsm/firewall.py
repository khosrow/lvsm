"""Firewall funcationality"""
import subprocess
import utils


class Firewall():
    def __init__(self, iptables):
        self.iptables = iptables

    def show(self, numeric):
        args = self.iptables + ' -L -v'
        if numeric:
            args = args + ' -n'
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            print stdout
            return True
        elif stderr:
            print stderr
        return False

    def show_virtual(self, host, numeric):
        args = self.iptables + ' -L INPUT'
        if numeric:
            args = args + ' -n'
            hostname = utils.gethostname(host)
        else:
            hostname = host
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            lines = stdout.split('\n')
            for line in lines:
                if line.find(" " + hostname) > -1:
                    print line
            return True
        elif stderr:
            print stderr
        return False
