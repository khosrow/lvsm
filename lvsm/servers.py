"""
Data classes for manipulating and storing server information.
Abstracts away having to deal with Real Servers and Virtual Servers.
And allows for easy printing of the info.
"""
import socket

# Local module
import termcolor

class Server():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


class Virtual(Server):
    def __init__(self, proto, ip, port, sched, persistence=None):
        Server.__init__(self, ip, port)
        self.proto = proto
        self.realServers = list()
        self.sched = sched
        self.persistence = persistence

    def __str__(self, numeric=True, color=False, real=None, port=None):
        """provide an easy way to print this object"""
        proto = self.proto.upper().ljust(4)
        host = self.ip
        service = self.port

        if self.proto.upper() == 'FWM':
            pass
        elif not numeric:
            try:
                try:
                    host, aliaslist, addrlist = socket.gethostbyaddr(self.ip)
                except socket.herror:
                    pass
                service = socket.getservbyport(int(self.port))
            except socket.error:
                pass
        if self.proto.upper() == 'FWM':
            ipport = host.ljust(40)
        else:
            ipport = (host + ":" + service).ljust(40)

        sched = self.sched.ljust(7)

        if self.persistence:            
            line = "%s %s %s persistence %s" % (proto, ipport, sched, self.persistence)
        else:
            line = "%s %s %s" % (proto, ipport, sched)

        if color:
            line = termcolor.colored(line, attrs=['bold'])

        output = [line]
        for r in self.realServers:
            if real:
                if r.ip == real:
                    if port:
                        if int(r.port) == port:
                            output = [line]
                            output.append(r.__str__(numeric,color))
                    else:
                        output = [line]
                        output.append(r.__str__(numeric,color))

            else:
                output.append(r.__str__(numeric, color))

        # If a real server is provided, don't return empty VIPs
        if real:
            if len(output) == 1:
                return ''

        # Add space between each VIP in the final output
        if output:
            output.append('')

        return '\n'.join(output)
        
class Real(Server):
    def __init__(self, ip, port, weight, method, active, inactive):
        Server.__init__(self, ip,port)
        self.weight = weight
        self.method = method
        self.active = active
        self.inactive = inactive

    def __str__(self, numeric=False, color=False):
        host = self.ip
        service = self.port
        if not numeric:
            try:
                host, aliaslist, addrlist = socket.gethostbyaddr(self.ip)
            except socket.herror:
                pass
            try:
                service = socket.getservbyport(int(self.port))
            except socket.error:
                pass
        ipport = (host + ":" + service).ljust(40)
        method = self.method.ljust(7)
        weight = self.weight.ljust(6)
        active = self.active.ljust(10)
        inactive = self.inactive.ljust(10)
        line = "  -> %s %s %s %s %s" % (ipport, method, weight, active, inactive)
        # line = "          %s %s  %s  %s  %s" % (ipport, method, weight, active, inactive)
        # if real server weight is zero, we highlight it as red
        if color and self.weight == '0':
            line = termcolor.colored(line, 'red')
        return line