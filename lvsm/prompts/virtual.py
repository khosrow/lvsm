"""Various levels of command line shells for accessing ipvs and iptables
functionality form one location."""

import sys
import plugins.firewall
import utils
import termcolor
import logging

from prompt import CommandPrompt


logger = logging.getLogger('lvsm')


class VirtualPrompt(CommandPrompt):
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        # Change the word delimiters so that - or . don't cause a new match
        try:
            import readline
            readline.set_completer_delims(' ')
        except ImportError:
            pass
        # super(CommandPrompt, self).__init__()
        CommandPrompt.__init__(self, config)
        self.modules = ['director', 'firewall', 'nat', 'virtual', 'real']
        self.protocols = ['tcp', 'udp', 'fwm']
        self.firewall = plugins.firewall.Firewall(self.config['iptables'])
        self.rawprompt = "lvsm(live)(virtual)# "
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

    def do_status(self,line):
        """
        \rDisplay status of all virtual servers
        """
        syntax = "\nstatus\n"
        numeric = self.settings['numeric']
        color = self.settings['color']

        if not line:
            d = self.director.show(numeric, color)
            f = self.firewall.show(numeric, color)
            utils.pager(self.config['pager'], d + f)
        else:
            print syntax            

    def do_show(self, line):
        """
        \rShow status of a virtual server
        \rsyntax: show tcp|udp|fwm <vip> <port>
        """
        syntax = "\nsyntax: show tcp|udp|fwm <vip> <port>\n"
        commands = line.split()
        numeric = self.settings['numeric']
        color = self.settings['color']
        
        if len(commands) == 3:
            protocol = commands[0]
            vip = commands[1]
            port = commands[2]
            if protocol in self.protocols:
                d = self.director.show_virtual(vip, port, protocol, numeric, color)
                f = self.firewall.show_virtual(vip, port, protocol, numeric, color)
                utils.pager(self.config['pager'], d + f)
            else:
                print syntax
        else:
            print syntax

    def complete_show(self, text, line, begidx, endidx):
        """Tab completion for the show command"""
        if len(line) < 8:
            completions = [p for p in self.protocols if p.startswith(text)]
        elif len(line.split()) == 2:
            prot = line.split()[1]
            virtuals = self.director.get_virtual(prot)
            if not text:
                completions = virtuals[:]
        elif len(line.split()) == 3 and text:
            prot = line.split()[1]
            virtuals = self.director.get_virtual(prot)
            completions = [p for p in virtuals if p.startswith(text)]

        return completions
