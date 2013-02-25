"""Firewall funcationality"""
import subprocess
import socket
import utils
import termcolor


class Firewall():
    def __init__(self, iptables):
        self.iptables = iptables

    def show(self, numeric, color):
        args = [self.iptables, "-L", "-v"]
        if numeric:
            args.append("-n")
        try:
            try:
                output = subprocess.check_output(args)
            # python 2.6 compatibility code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return

        if color:
            result = list()
            for line in output.split('\n'):
                if 'Chain' not in line and 'ACCEPT' in line:
                    result.append(termcolor.colored(line, 'green'))
                elif 'Chain' not in line and ('REJECT' in line or 'DROP' in line):
                    result.append(termcolor.colored(line, 'red'))
                else:
                    result.append(line)
        else:
            result = output.split('\n')

        return result

    def show_nat(self, numeric):
        args = [self.iptables, "-t", "nat", "-L"]
        if numeric:
            args.append("-n")
        try:
            try:
                output = subprocess.check_output(args)
            # python 2.6 compatibility code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            print ("[ERROR] problem with iptables - " + e.strerror)
            return
        return output.split("\n")

    def show_virtual(self, host, port, protocol, numeric, color):
        result = list()
        args = [self.iptables, '-L', 'INPUT']
        if numeric:
            args.append('-n')
            hostname = utils.gethostname(host)
            portname = utils.getportnum(port)
        else:
            hostname = socket.getfqdn(host)
            portname = port
        try:
            try:
                output = subprocess.check_output(args)
            # python 2.6 compatibility code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            print "[ERROR] problem with iptables - " + e.strerror
            return
        if output:
            lines = output.split('\n')
            for line in lines:
                # break the iptables output into tokens
                # assumptions:
                # 2nd item is the protocol
                # 5th item is the hostname
                # 8th item is the portname
                tokens = line.split()
                if len(tokens) >= 7:
                    if ((tokens[1] == protocol or tokens[2] == "all") and
                        tokens[4] == hostname and
                        tokens[6] == "dpt:" + str(portname)):
                        if color:
                            if line.startswith('ACCEPT'):
                                result.append(termcolor.colored(line, 'green'))
                            elif (line.startswith('REJECT') or
                                  line.startswith('DROP')):
                                result.append(termcolor.colored(line, 'red'))
                            else:
                                result.append(line)
                        else:
                            result.append(line)
        return result
