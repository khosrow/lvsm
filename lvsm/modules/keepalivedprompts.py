import logging
import sys
from lvsm import shell

logger = logging.getLogger('lvsm')

class VirtualPrompt(shell.VirtualPrompt):
    """
    Display information about virtual IP with keepalived specific functions.
    """
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        shell.VirtualPrompt.__init__(self, config)

    # def do_disable(self, line):
    #     """
    #     \rDisable real server belonging to a VIP.
    #     \rsyntax: disable tcp|udp|fwm <vip> <port> real <real> <port>
    #     """

    #     syntax = "syntax: disable tcp|udp|fwm <vip> <port> real <real> <port>"

    #     commands = line.split()
    #     if len(commands) == 6:
    #         module = commands[0]
    #         vip = commands[1]
    #         vport = commands[2]
    #         rip = commands[4]
    #         rport = commands[5]
    #         print "Disabling real: %s:%s" % (rip, rport)
    #     else:
    #         print "\n%s\n" % syntax

    # def do_enable(self, line):
    #     """
    #     \renable real server belonging to a VIP.
    #     \rsyntax: enable tcp|udp|fwm <vip> <port> real <real> <port>
    #     """

    #     syntax = "syntax: enable tcp|udp|fwm <vip> <port> real <real> <port>"

    #     commands = line.split()
    #     if len(commands) == 6:
    #         module = commands[0]
    #         vip = commands[1]
    #         vport = commands[2]
    #         rip = commands[4]
    #         rport = commands[5]
    #         print "enabling real: %s:%s" % (rip, rport)
    #     else:
    #         print "\n%s\n" % syntax

class RealPrompt(shell.RealPrompt):
    """
    Display information about real servers with keepalived specific functions.
    """
    def __init__(self, config, rawprompt='', stdin=sys.stdin, stdout=sys.stdout):
        shell.RealPrompt.__init__(self, config)

    def do_disable(self, line):
        """
        \rDisable real server across VIPs.
        \rsyntax: disable tcp|udp|fwm <rip> [<port>] [<vip> <port>]
        """

        syntax = "*** Syntax: disable tcp|udp|fwm <rip> [<port>] [<vip> <port>]"

        # Some default values to be used
        port = ''
        vip = ''
        vport = ''
        commands = line.split()
        if len(commands) < 2 or len(commands) > 5:
            print syntax
        elif len(commands) >= 2:
            protocol = commands[0]
            # Verify protocol is valid
            if protocol not in self.protocols:
                print syntax 
                return 

            host = commands[1]
            if len(commands) == 3:
                port = commands[2]
                if len(commands) == 4:
                    vip = commands[3]
                    if len(commands) == 5:
                        vport = commands[4]

            # ask for an optional reason for disabling
            reason = raw_input("Reason for disabling [default = None]: ")
            # if not self.director.disable(host, port, reason=reason):
            if not self.director.disable(protocol,
                                         host, port,
                                         vip, vport,
                                         reason=reason):
                logger.error("Could not disable %s" % host)
        else:
            print syntax

    def do_enable(self, line):
        """
        \rEnable real server across VIPs.
        \rsyntax: enable tcp|udp|fwm <rip> [<port>] [<vip> <port>]
        """

        syntax = "*** Syntax: enable tcp|udp|fwm <rip> [<port>] [<vip> <port>]"

        # Some default values to be used
        port = ''
        vip = ''
        vport = ''

        commands = line.split()
        if len(commands) < 2 or len(commands) > 5:
            print syntax
        elif len(commands) >= 2:
            protocol = commands[0]
            # Verify protocol is valid
            if protocol not in self.protocols:
                print syntax
                return

            host = commands[1]
            if len(commands) == 3:
                port = commands[2]
            elif len(commands) == 4:
                vip = commands[3]
                if len(commands) == 5:
                    vport = commands[4]

            if not self.director.enable(protocol,
                                        host, port,
                                        vip, vport):
                logger.error("Could not enable %s" % host)
        else:
            print syntax

    def complete_disable(self, text, line, begidx, endidx):
        """Tab completion for the disable command"""
        tokens = line.split()
        if len(line) < 12:
            completions = [p for p in self.protocols if p.startswith(text)]
        elif len(tokens) == 2:
            prot = tokens[1]
            reals = self.director.get_real(prot)
            if not text:
                completions = reals[:]
        elif len(tokens) == 3 and text:
            prot = tokens[1]
            reals = self.director.get_real(prot)
            completions = [p for p in reals if p.startswith(text)]
        elif len(tokens) == 4 and not text:
            prot = tokens[1]
            virtuals = self.director.get_virtual(prot)
            completions = virtuals[:]
        elif len(tokens) == 5 and text:
            virtuals = self.director.get_virtual(prot)
            completions = [p for p in virtuals if p.startswith(text)]
        else:
            completions = list()

        return completions

    def complete_enable(self, text, line, begidx, endidx):
        """Tab completion for the disable command"""
        tokens = line.split()
        if len(line) < 11:
            completions = [p for p in self.protocols if p.startswith(text)]
        elif len(tokens) == 2 and not text:
            prot = tokens[1]
            reals = self.director.get_real(prot)
            completions = reals[:]
        elif len(tokens) == 3 and text:
            prot = tokens[1]
            reals = self.director.get_real(prot)
            completions = [p for p in reals if p.startswith(text)]
        elif len(tokens) == 4 and not text:
            prot = tokens[1]
            virtuals = self.director.get_virtual(prot)
            completions = virtuals[:]
        elif len(tokens) == 5 and text:
            prot = tokens[1]
            virtuals = self.director.get_virtual(prot)
            completions = [p for p in virtuals if p.startswith(text)]
        else:
            completions = list()

        return completions