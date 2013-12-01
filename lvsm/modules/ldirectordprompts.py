import sys
from lvsm import shell

class VirtualPrompt(shell.VirtualPrompt):
    """
    Display information about virtual IP with ldirector specific fucntions.
    """
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        shell.VirtualPrompt.__init__(self, config)

    def do_welcome(self,line):
        """Being polite"""
        print "Welcome!"
