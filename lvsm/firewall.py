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

    def show_virtual(self, host, port, numeric):
        args = self.iptables + ' -L INPUT'
        if numeric:
            args = args + ' -n'
            hostname = utils.gethostname(host)
            portname = utils.getportnum(port)
        else:
            hostname = host
            portname = port
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return False
        stdout, stderr = proc.communicate()
        if stdout:
            lines = stdout.split('\n')
            for line in lines:
                # break the iptables output into tokens
                # assumptions:
                # 5th item is the hostname
                # 8th item is the portname
                tokens = line.split()
                if len(tokens) >= 7:
                    if (tokens[4] == hostname and
                        tokens[6] == "dpt:" + portname):
                        print line
            return True
        elif stderr:
            print stderr
        return False
