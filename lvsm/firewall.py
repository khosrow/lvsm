"""Firewall funcationality"""
import subprocess
import socket
import utils
import termcolor
import logging

logger = logging.getLogger('lvsm')


class Firewall():
    def __init__(self, iptables):
        self.iptables = iptables

    def show(self, numeric, color):
        args = [self.iptables, "-L", "-v"]
        if numeric:
            args.append("-n")
        try:
            try:
                logger.info("Running: %s" % " ".join(args))
                output = subprocess.check_output(args)
            # python 2.6 compatibility code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            logger.error("problem with iptables - %s : %s" % (e.strerror , args[0]))
            return list()

        result = ['', 'IP Packet filter rules']
        result += ['======================']
        if color:
            for line in output.split('\n'):
                if 'Chain' not in line and 'ACCEPT' in line:
                    result.append(termcolor.colored(line, 'green'))
                elif 'Chain' not in line and ('REJECT' in line or 'DROP' in line):
                    result.append(termcolor.colored(line, 'red'))
                else:
                    result.append(line)
        else:
            result += output.split('\n')

        return result

    def show_nat(self, numeric):
        args = [self.iptables, "-t", "nat", "-L", "-v"]
        if numeric:
            args.append("-n")
        try:
            try:
                logger.info("Running: %s" % " ".join(args))
                output = subprocess.check_output(args)
            # python 2.6 compatibility code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            logger.error("Problem with iptables - %s : %s " % (e.strerror, args[0]))
            return list()
        result = ['', 'NAT rules', '=========']
        result += output.split('\n')
        return result

    def show_mangle(self, numeric, color, fwm=None):
        """Show the iptables mangle table"""
        args = [self.iptables, '-t', 'mangle', '-L', '-v']
        if numeric:
            args.append('-n')

        try:
            try:
                logger.info("Running: %s" % " ".join(args))
                output = subprocess.check_output(args)
            # python 2.6 compat code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            logger.error("Problem with iptables - %s : %s" % (e.strerror, args[0]))
            return list()

        result = list()
        if output:
            lines = output.split('\n')

            # Find which column contains the destination 
            #header = lines[1].split() 
            #try:
            #    index = header.index('destination')  
            #except ValueError as e:
            #    index = -1

            for line in lines:
                tokens = line.split() 
                if fwm and hex(fwm) in tokens:
                    result.append(line)
                else:
                    result.append(line)

        result.insert(0, '')
        result.insert(1, 'Mangle rules')
        result.insert(2, '============')
        return result 

    def show_virtual(self, host, port, protocol, numeric, color):
        result = list()
        args = [self.iptables, '-L', 'INPUT']
        if port:
            portnum = utils.getportnum(port)
            try:
                portname = socket.getservbyport(int(portnum))
            except socket.error:
                portname = portnum
            except OverflowError as e:
                logger.error("%s" % e)
                return list() 

        if numeric:
            args.append('-n')
            hostnames = utils.gethostbyname_ex(host)
        else:
            # Turn this into a list so it behaves like the above case
            # And we only perform a list membership check
            hostnames = [socket.getfqdn(host)]

        # Nested try/except needed to catch exceptions in the "Except"    
        try:
            try:
                logger.info("Running: %s" % " ".join(args))
                output = subprocess.check_output(args)
            # python 2.6 compatibility code
            except AttributeError as e:
                output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        except OSError as e:
            logger.error("Problem with iptables - %s : %s" % (e.strerror, args[0]))
            return list()
        if output:
            lines = output.split('\n')
            for line in lines:
                # break the iptables output into tokens
                # assumptions:
                # 2nd item is the protocol - tokens[1]
                # 5th item is the hostname - tokens[4]
                # 7th item is the portname - tokens[6]
                tokens = line.split()

                if len(tokens) >= 7:
                    if ((tokens[1] == protocol or tokens[2] == "all") and
                        tokens[4] in hostnames and
                        ( not port or (tokens[6] == "dpt:" + str(portname) or tokens[6] == "dpt:" + str(portnum)))
                        ):
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
            # If we have any output, let's also display some headers
            if result:
                result.insert(0, '')
                result.insert(1, 'IP Packet filter rules')
                result.insert(2, '======================')
                
        return result
