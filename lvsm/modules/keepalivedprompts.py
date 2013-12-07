import sys
from lvsm import shell

class VirtualPrompt(shell.VirtualPrompt):
    """
    Display information about virtual IP with ldirector specific fucntions.
    """
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        shell.VirtualPrompt.__init__(self, config)

    def do_disable(self, line):
        """
        \rDisable real server belonging to a VIP.
        \rsyntax: disable tcp|udp|fwm <vip> <port> real <real> <port>
        """

        syntax = "syntax: disable tcp|udp|fwm <vip> <port> real <real> <port>"

        commands = line.split()
        if len(commands) == 6:
            module = commands[0]
            vip = commands[1]
            vport = commands[2]
            rip = commands[4]
            rport = commands[5]
            print "Disabling real: %s:%s" % (rip, rport)
        else:
            print "\n%s\n" % syntax
