"""Various levels of command line shells for accessing ipvs and iptables
functionality form one location."""

import cmd
import getpass
import subprocess
import sys
import socket
import lvsdirector
import firewall
import utils
import termcolor

DEBUG = False


class CommandPrompt(cmd.Cmd):
    settings = {'numeric': False,
                'color': True}
    variables = ['numeric', 'color']
    rawprompt = ''

    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        cmd.Cmd.__init__(self)
        self.config = config

    def help_help(self):
        print
        print "show help"

    def do_exit(self, line):
        """exit from lvsm shell"""
        print "goodbye."
        sys.exit(0)

    def do_quit(self, line):
        """exit from lvsm shell"""
        print "goodbye."
        sys.exit(0)

    def do_end(self, line):
        """return to previous context"""
        #print
        return True

    def do_set(self, line):
        """set or display different variables

        syntax: set [<variable>] [<value>]
        <variable> can be one of
        numeric on|off          Toggle numeric ipvsadm display ON/OFF
        color on|off            Toggle color display ON/OFF"""
        if not line:
            print
            print "Shell Settings"
            print "=============="
            for key, value in self.settings.items():
                print str(key) + " : " + str(value)
            print
        else:
            tokens = line.split()
            if len(tokens) == 2:
                if tokens[0] == "numeric":
                    if tokens[1] == "on":
                        self.settings['numeric'] = True
                    elif tokens[1] == "off":
                        self.settings['numeric'] = False
                    else:
                        print "Usage: set numeric on|off"
                elif tokens[0] == "color":
                    if tokens[1] == "on":
                        self.settings['color'] = True
                        self.prompt = termcolor.colored(self.rawprompt, "red",
                                                        attrs=["bold"])
                    elif tokens[1] == "off":
                        self.settings['color'] = False
                        self.prompt = self.rawprompt
                    else:
                        print "Usage: set color on|off"
                else:
                    print self.do_set.__doc__
            else:
                print self.do_set.__doc__

    def complete_set(self, text, line, begidx, endidx):
        """Tab completion for the set command"""
        if len(line) < 12:
            if not text:
                    completions = self.variables[:]
            else:
                completions = [m for m in self.variables if m.startswith(text)]
        else:
            completions = []
        return completions

    def emptyline(self):
        """Override the default emptyline and return a blank line"""
        pass

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        # check to see if the prompt should be colorized
        if self.settings['color']:
            self.prompt = termcolor.colored(self.rawprompt, "red",
                                            attrs=["bold"])
        else:
            self.prompt = self.rawprompt
        return stop


class MainPrompt(CommandPrompt):
    """Class to handle the top level prompt in lvsm"""
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        cmd.Cmd.__init__(self)
        self.config = config
        self.modules = ['director', 'firewall']
        self.rawprompt = "lvsm# "
        if self.settings['color']:
            c = "red"
            a = ["bold"]
        else:
            c = None
            a = None
        self.prompt = termcolor.colored("lvsm# ", color=c, attrs=a)

    def do_configure(self, line):
        """The configuration level

        Items related to configuration of IPVS and iptables are available here.
        """
        commands = line.split()
        configshell = ConfigurePrompt(self.config)
        if not line:
            configshell.cmdloop()
        else:
            configshell.onecmd(' '.join(commands[0:]))

    def do_status(self, line):
        """The status level.

        Running status of IPVS and iptables are available here.
        """
        commands = line.split()
        statshell = StatusPrompt(self.config)
        if not line:
            statshell.cmdloop()
        else:
            statshell.onecmd(' '.join(commands[0:]))

    def do_restart(self, line):
        """restart the given module.

        Module must be one of director or firewall.

        syntax: restart director|firewall
        """
        if line == "director":
            if self.config['director_cmd']:
                print "restaring director"
                try:
                    result = subprocess.call(self.config['director_cmd'],
                                             shell=True)
                except OSError as e:
                    print "[ERROR] problem restaring director - " + e.strerror
            else:
                print "[ERROR] 'director_cmd' not defined in config!"
        elif line == "firewall":
            if self.config['firewall_cmd']:
                print "restarting firewall"
                try:
                    result = subprocess.call(self.config['firewall_cmd'],
                                             shell=True)
                except OSError as e:
                    print "[ERROR] problem restaring firewall - " + e.strerror
            else:
                print "[ERROR] 'firewall_cmd' not defined in config!"
        else:
            print "Usage: restart firewall|director"

    def complete_restart(self, text, line, begix, endidx):
        """Tab completion for restart command"""
        if len(line) < 17:
            if not text:
                completions = self.modules[:]
            else:
                completions = [m for m in self.modules if m.startswith(text)]
        else:
            completions = []
        return completions


class ConfigurePrompt(CommandPrompt):
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        cmd.Cmd.__init__(self)
        self.config = config
        self.modules = ['director', 'firewall']
        self.rawprompt = "lvsm(configure)# "
        if self.settings['color']:
            c = "red"
            a = ["bold"]
        else:
            c = None
            a = None
        self.prompt = termcolor.colored("lvsm(configure)# ", color=c,
                                        attrs=a)

    def print_config(self, configkey):
        """prints out the specified configuration file"""
        if not self.config[configkey]:
            print "[ERROR] '" + configkey + "' not defined in config file!"
        else:
            lines = utils.print_file(self.config[configkey])
            for line in lines:
                print line.rstrip()

    def svn_sync(self, filename, username, password):
        cluster_command = ''
        if self.config['dsh_group']:
            cluster_command = 'dsh -g ' + self.config['dsh_group'] + ' '
        # commit code
        args = ('svn commit --username ' + username + ' --password ' +
                password + ' ' + filename)
        try:
            result = subprocess.call(args, shell=True)
        except OSError as e:
            print "[ERROR] problem with configuration sync - " + e.strerror
        # utils.execute(args, "problem with configuration sync")
        # now update on all the nodes in the cluster
        args = (cluster_command + 'svn update --username ' + username +
                ' --password ' + password + ' ' + filename)
        # utils.execute(args, "problem with configuration sync")
        try:
            result = subprocess.call(args, shell=True)
        except OSError as e:
            print "[ERROR] problem with configuration sync - " + e.strerror

    def complete_show(self, text, line, begidx, endidx):
        """Tab completion for the show command"""
        if len(line) < 14:
            if not text:
                completions = self.modules[:]
            else:
                completions = [m for m in self.modules if m.startswith(text)]
        else:
            completions = []
        return completions

    def do_show(self, line):
        """Show configuration for an item. The configuration files are \
        defined in lvsm.conf

        syntax: show <module>
        <module> can be one of the following
        director                the IPVS director config file
        firewall                the iptables firewall config file
        """
        if line == "director":
            self.print_config("director_config")
        elif line == "firewall":
            self.print_config("firewall_config")
        else:
            print self.do_show.__doc__

    def complete_edit(self, text, line, begidx, endidx):
        """Tab completion for the show command"""
        if len(line) < 14:
            if not text:
                completions = self.modules[:]
            else:
                completions = [m for m in self.modules if m.startswith(text)]
        else:
            completions = []
        return completions

    def do_edit(self, line):
        """Edit the configuration of an item. The configuration files are \
        defined in lvsm.conf

        edit <module>
        <module> can be one of the follwoing
        director                the IPVS director config file
        firewall                the iptables firewall config file
        """
        if line == "director" or line == "firewall":
            key = line + "_config"
            filename = self.config[key]
            if not filename:
                print "[ERROR] '" + key + "' not defined in config file!"
            else:
                args = "vi " + filename
                utils.log(str(args))
                result = subprocess.call(args, shell=True)
                if result != 0:
                    print "[ERROR] something happened during the edit of " +\
                          config[line]
        else:
            print self.do_edit.__doc__

    def do_sync(self, line):
        """Sync all configuration files across the cluster."""
        if line:
            print self.do_sync.__doc__
        else:
            # ask for username and passwd so user isn't bugged on each server
            username = raw_input("Enter SVN username: ")
            password = getpass.getpass("Enter SVN password: ")
            # update director config
            if self.config['director_config']:
                print "Syncing " + self.config['director_config'] + " ..."
                self.svn_sync(self.config['director_config'],
                              username, password)
            # update firewall config
            if self.config['firewall_config']:
                print "Syncing " + self.config['firewall_config'] + " ..."
                self.svn_sync(self.config['firewall_config'],
                              username, password)


class StatusPrompt(CommandPrompt):
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        cmd.Cmd.__init__(self)
        self.config = config
        self.modules = ['director', 'firewall', 'virtual', 'real']
        self.protocols = ['tcp', 'udp', 'fwm']
        self.director = lvsdirector.Director(self.config['director'],
                                             self.config['maintenance_dir'],
                                             self.config['ipvsadm'])
        self.firewall = firewall.Firewall(self.config['iptables'])
        self.rawprompt = "lvsm(status)# "
        if self.settings['color']:
            c = "red"
            a = ["bold"]
        else:
            c = None
            a = None
        self.prompt = termcolor.colored("lvsm(status)# ", color=c,
                                        attrs=a)

    def complete_show(self, text, line, begidx, endidx):
        """Tab completion for the show command"""
        if line.startswith("show virtual "):
            if line == "show virtual ":
                completions = self.protocols[:]
            elif len(line) < 16:
                completions = [p for p in self.protocols if p.startswith(text)]
            else:
                completions = []
        elif (line.startswith("show director") or
              line.startswith("show firewall") or
              line.startswith("show real")):
            completions = []
        elif not text:
            completions = self.modules[:]
        else:
            completions = [m for m in self.modules if m.startswith(text)]
        return completions

    def do_show(self, line):
        """Show information about a specific item.

        syntax: show <module>
        <module> can be one of the following
        director                the running ipvs status
        firewall                the iptables firewall status
        real <server> <port>    the status of a realserver
        virtual tcp|udp|fwm <vip> <port>    the status of a specific VIP
        """
        commands = line.split()
        if line == "director":
            self.director.show(self.settings['numeric'])
        elif line == "firewall":
            self.firewall.show(self.settings['numeric'])
        elif line.startswith("virtual"):
            if len(commands) == 4:
                protocol = commands[1]
                vip = commands[2]
                port = commands[3]
                if protocol in self.protocols:
                    if self.director.show_virtual(vip, port, protocol,
                                                  self.settings['numeric']):
                        self.firewall.show_virtual(vip, port,
                                                   self.settings['numeric'])
                else:
                    print "Usage: virtual tcp|udp|fwm <vip> <port>"
            else:
                print "Usage: virtual tcp|udp|fwm <vip> <port>"
        elif line.startswith("real"):
            if len(commands) == 3:
                host = commands[1]
                port = commands[2]
                self.director.show_real(host, port, self.settings['numeric'])
            else:
                print "Usage: real <server> <port>"
        else:
            print self.do_show.__doc__

    def complete_disable(self, text, line, begidx, endidx):
        """Tab completion for disable command"""
        servers = ['real', 'virtual']
        if  (line.startswith("disable real") or
             line.startswith("disable virtual")):
            completions = []
        elif not text:
            completions = servers[:]
        else:
            completions = [s for s in servers if s.startswith(text)]
        return completions

    def do_disable(self, line):
        """Disable a real or virtual server.

        syntax: disable real|virtual <host> [<port>]
        """
        commands = line.split()
        # ask for an optional reason for disabling
        reason = raw_input("Reason for disabling [default = None]: ")
        if len(commands) < 2 or len(commands) > 3:
            print self.do_disable.__doc__
        elif line.startswith("virtual"):
            host = commands[1]
            print "Not implemented yet!"
        elif line.startswith("real"):
            host = commands[1]
            if len(commands) == 2:
                port = ''
            elif len(commands) == 3:
                port = commands[2]
            else:
                print "Usage: disable real <host> [<port>]"
                return
            if not self.director.disable(host, port, reason):
                print "[ERROR] could not disable " + host
        else:
            print self.do_disable.__doc__

    def complete_enable(self, text, line, begidx, endidx):
        """Tab completion for enable command"""
        servers = ['real', 'virtual']
        if  (line.startswith("enable real") or
             line.startswith("enable virtual")):
            completions = []
        elif not text:
            completions = servers[:]
        else:
            completions = [s for s in servers if s.startswith(text)]
        return completions

    def do_enable(self, line):
        """Enable a real or virtual server.

        syntax: enable real|virtual <host> [<port>]
        """
        commands = line.split()
        if len(commands) < 2 or len(commands) > 3:
            print self.do_enable.__doc__
        elif line.startswith("virtual"):
            host = commands[1]
            print "Not implemented yet!"
        elif line.startswith("real"):
            host = commands[1]
            if len(commands) == 2:
                port = ''
            elif len(commands) == 3:
                port = commands[2]
            else:
                print "Usage: enable real <host> [<port>]"
                return
            if not self.director.enable(host, port):
                print "[ERROR] could not enable " + host
        else:
            print self.do_enable.__doc__
