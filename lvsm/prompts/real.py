"""Various levels of command line shells for accessing ipvs and iptables
functionality form one location."""

import sys
import plugins.firewall
import utils
import termcolor
import logging

from prompt import CommandPrompt

logger = logging.getLogger('lvsm')


class RealPrompt(CommandPrompt):
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        CommandPrompt.__init__(self, config)
        self.modules = ['director', 'firewall', 'nat', 'virtual', 'real']
        self.protocols = ['tcp', 'udp', 'fwm']
        self.firewall = plugins.firewall.Firewall(self.config['iptables'])
        self.rawprompt = "lvsm(live)(real)# "
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

    def do_show(self, line):
        """Show information about a specific real server."""
        syntax = "\nsyntax: show <server> <port>\n"
        commands = line.split()
        numeric = self.settings['numeric']
        color = self.settings['color']
        if len(commands) == 2:
            host = commands[0]
            port = commands[1]
            utils.pager(self.config['pager'], self.director.show_real(host, port, numeric, color))
        else:
            print syntax

    def do_disable(self, line):
        """Disable a real or virtual server."""
        syntax = "\nsyntax: disable <host> [<port>]\n"
        commands = line.split()
        if len(commands) > 2:
            print syntax
        elif len(commands) <= 2:
            host = commands[0]
            if len(commands) == 1:
                port = ''
            elif len(commands) == 2:
                port = commands[1]
            else:
                print syntax
                return
            # ask for an optional reason for disabling
            reason = raw_input("Reason for disabling [default = None]: ")
            if not self.director.disable(host, port, reason):
                logger.error("Could not disable %s" % host)
        else:
            print syntax

    def do_enable(self, line):
        """Enable a real or virtual server."""
        syntax = "\nsyntax: enable <host> [<port>]\n"
        commands = line.split()
        if len(commands) > 2:
            print syntax
        elif len(commands) <= 2:
            host = commands[0]
            if len(commands) == 1:
                port = ''
            elif len(commands) == 2:
                port = commands[0]
            else:
                print syntax
                return
            if not self.director.enable(host, port):
                logger.error("Could not enable %s" % host)
        else:
            print syntax

    def help_show(self):
        print ""
        print "Show information about a specific real server."
        print "syntax: show <server> <port>"
        print ""

    def help_disable(self):
        print ""
        print "Disable a real server."
        print "syntax: disable <host> [<port>]"
        print ""

    def help_enable(self):
        print ""
        print "Enable a real server."
        print "syntax: enable <host> [<port>]"
        print ""

    # def complete_show(self, text, line, begidx, endidx):
    #     """Tab completion for the show command"""
    #     if line.startswith("show virtual "):
    #         if line == "show virtual ":
    #             completions = self.protocols[:]
    #         elif len(line) < 16:
    #             completions = [p for p in self.protocols if p.startswith(text)]
    #         # elif line.startswith("show virtual ") and len(line) > 16:
    #             # completions = [p for p in self.director.get_virutal('tcp') if p.startswith(text)]
    #         # elif line == "show virtual tcp ":
    #         #     virtuals = self.director.get_virtual('tcp')
    #         #     completions = [p for p in virtuals if p.startswith(text)]
    #         # elif line == "show virtual tcp ":
    #         elif line.startswith("show virtual tcp "):
    #             virtuals = self.director.get_virtual('tcp')
    #             completions = [p for p in virtuals if p.startswith(text)]
    #         elif line == "show virtual udp ":
    #             virtuals = self.director.get_virtual('udp')
    #             completions = [p for p in virtuals if p.startswith(text)]
    #         else:
    #             completions = []
    #     elif (line.startswith("show director") or
    #           line.startswith("show firewall") or
    #           line.startswith("show nat") or
    #           line.startswith("show real")):
    #         completions = []
    #     elif not text:
    #         completions = self.modules[:]
    #     else:
    #         completions = [m for m in self.modules if m.startswith(text)]
    #     return completions

    # def complete_disable(self, text, line, begidx, endidx):
    #     """Tab completion for disable command."""
    #     servers = ['real', 'virtual']
    #     if  (line.startswith("disable real") or
    #          line.startswith("disable virtual")):
    #         completions = []
    #     elif not text:
    #         completions = servers[:]
    #     else:
    #         completions = [s for s in servers if s.startswith(text)]
    #     return completions

    # def complete_enable(self, text, line, begidx, endidx):
    #     """Tab completion for enable command."""
    #     if  (line.startswith("enable real") or
    #          line.startswith("enable virtual")):
    #         completions = []
    #     elif not text:
    #         completions = servers[:]
    #     else:
    #         completions = [s for s in servers if s.startswith(text)]
    #     return completions
