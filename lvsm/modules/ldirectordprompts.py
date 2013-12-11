import logging
import sys
from lvsm import shell

logger = logging.getLogger('lvsm')

class VirtualPrompt(shell.VirtualPrompt):
    """
    Display information about virtual IP with ldirector specific fucntions.
    """
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        shell.VirtualPrompt.__init__(self, config)

    # def do_disable(self, line):
    #     """
    #     \rDisable real server across VIPs.
    #     \rsyntax: disable <rip> <port>
    #     """

    #     syntax = "syntax: disable <rip> <port>"

    #     commands = line.split()
    #     if len(commands) > 2 or len(commands) == 0:
    #         print syntax
    #     elif len(commands) <= 2:
    #         host = commands[0]
    #         if len(commands) == 1:
    #             port = ''
    #         elif len(commands) == 2:
    #             port = commands[1]
    #         else:
    #             print syntax
    #             return
    #         # ask for an optional reason for disabling
    #         reason = raw_input("Reason for disabling [default = None]: ")
    #         if not self.director.disable(host, port, reason):
    #             logger.error("Could not disable %s" % host)
    #     else:
    #         print syntax

    # def do_enable(self, line):
    #     """
    #     \rEnable real server across VIPs.
    #     \rsyntax: enable <rip> <port>
    #     """

    #     syntax = "syntax: enable <rip> <port>"

    #     commands = line.split()
    #     if len(commands) > 2 or len(commands) == 0:
    #         print syntax
    #     elif len(commands) <= 2:
    #         host = commands[0]
    #         if len(commands) == 1:
    #             port = ''
    #         elif len(commands) == 2:
    #             port = commands[0]
    #         else:
    #             print syntax
    #             return
    #         if not self.director.enable(host, port):
    #             logger.error("Could not enable %s" % host)
    #     else:
    #         print syntax