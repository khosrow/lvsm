import subprocess
import sys
import logging

from lvsm import firewall, termcolor
from lvsm.prompts import configure, virtual, real, prompt

logger = logging.getLogger('lvsm')


class LivePrompt(prompt.CommandPrompt):
    """
    Class for the live command prompt. This is the main landing point
    and is called from __main__.py
    """
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        prompt.CommandPrompt.__init__(self, config)
        self.modules = ['director', 'firewall', 'nat', 'virtual', 'real']
        self.protocols = ['tcp', 'udp', 'fwm']
        self.firewall = firewall.Firewall(self.config['iptables'])
        self.rawprompt = "lvsm(live)# "
        if self.settings['color']:
            c = "red"
            # c = None
            a = ["bold"]
            # a = None
        else:
            c = None
            a = None
        self.prompt = termcolor.colored(self.rawprompt, color=c,
                                        attrs=a)

    def do_configure(self, line):
        """Enter configuration level."""
        commands = line.split()
        # configshell = prompts.configure.ConfigurePrompt(self.config)
        configshell = configure.ConfigurePrompt(self.config)
        if not line:
            configshell.cmdloop()
        else:
            configshell.onecmd(' '.join(commands[0:]))

    def do_virtual(self, line):
        """
        \rVirtual IP level. 
        \rLevel providing information on virtual IPs
        """
        commands = line.split()
        # virtualshell = prompts.virtual.VirtualPrompt(self.config)
        virtualshell = virtual.VirtualPrompt(self.config)
        if not line:
            virtualshell.cmdloop()
        else:
            virtualshell.onecmd(' '.join(commands[0:]))

    def do_real(self,line):
        """
        \rReal Server level.
        \rLevel providing information on real servers
        """
        commands = line.split()
        # realshell = prompts.real.RealPrompt(self.config)
        realshell = real.RealPrompt(self.config)
        if not line:
            realshell.cmdloop()
        else:
            realshell.onecmd(' '.join(commands[0:]))

    def do_restart(self, line):
        """Restart the direcotr or firewall module."""
        if line == "director":
            if self.config['director_cmd']:
                print "restaring director"
                try:
                    subprocess.call(self.config['director_cmd'], shell=True)
                except OSError as e:
                    logger.error("probmel while restaring director - %s" % e.strerror)
            else:
                logger.error("'director_cmd' not defined in lvsm configuration!")
        elif line == "firewall":
            if self.config['firewall_cmd']:
                print "restarting firewall"
                try:
                    subprocess.call(self.config['firewall_cmd'], shell=True)
                except OSError as e:
                    logger.error("problem restaring firewall - %s" % e.strerror)
            else:
                logger.error("'firewall_cmd' not defined in lvsm configuration!")
        else:
            print "syntax: restart firewall|director"

    def help_configure(self):
        print ""
        print "The configuration level."
        print "Items related to configuration of IPVS and iptables are available here."
        print ""

    def help_restart(self):
        print "Restart the given module."
        print ""
        print "Module must be one of director or firewall."
        print ""
        print "syntax: restart director|firewall"

    def complete_restart(self, text, line, begix, endidx):
        """Tab completion for restart command."""
        if len(line) < 17:
            if not text:
                completions = self.modules[:]
            else:
                completions = [m for m in self.modules if m.startswith(text)]
        else:
            completions = []
        return completions
