"""Firewall funcationality"""
import subprocess
import utils


class Firewall():
    def __init__(self, iptables):
        self.iptables = iptables

    def show(self, numeric):
        args = [self.iptables, "-L", "-v"]
        if numeric:
            args.append("-n")
        try:
            output = subprocess.check_output(args)
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return
        return output.split("\n")

    def show_virtual(self, host, port, numeric):
        result = list()
        args = [self.iptables, '-L', 'INPUT']
        if numeric:
            args.append('-n')
            hostname = utils.gethostname(host)
            portname = utils.getportnum(port)
        else:
            hostname = host
            portname = port
        try:
            output = subprocess.check_output(args)
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return
        if output:            
            lines = output.split('\n')
            for line in lines:
                # break the iptables output into tokens
                # assumptions:
                # 5th item is the hostname
                # 8th item is the portname
                tokens = line.split()
                if len(tokens) >= 7:
                    if (tokens[4] == hostname and
                        tokens[6] == "dpt:" + portname):                        
                        result.append(line)
        return result
