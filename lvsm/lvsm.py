"""Various levels of command line shells for accessing ipvs and iptables
functionality form one location."""

import cmd
import getpass
import subprocess
import os
import sys
import lvsdirector
import socket

DEBUG = False


def log(msg):
    if DEBUG:
        print "[DEBUG] " + msg


def execute(args, error, pipe=False):
    """Simple wrapper for subprocess.Popen"""
    try:
        log(str(args))
        if pipe:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
        else:
            result = subprocess.call(args, shell=True)
    except OSError as e:
        print "[ERROR] " + error + " - " + e.strerror
    else:
        if pipe:
            stdout, stderr = proc.communicate()
            if stdout:
                print stdout
            elif stderr:
                print stderr


class CommandPrompt(cmd.Cmd):
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
        print
        return True


class MainPrompt(CommandPrompt):
    """Class to handle the top level prompt in lvsm"""
    prompt = "lvsm# "

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


class ConfigurePrompt(CommandPrompt):
    prompt = "lvsm(configure)# "
    modules = ['director', 'firewall']

    def print_config(self, configkey):
        """prints out the specified configuration file"""
        lines = list()
        try:
            file = open(self.config[configkey])
            lines = file.readlines()
            file.close()
        except IOError as e:
            print "[ERROR] Unable to read '" + e.filename + "'"
            print "[ERROR] " + e.strerror
        for line in lines:
            print line.rstrip()

    def svn_sync(self, filename, username, password):
        cluster_command = ''
        if self.config['dsh_group']:
            cluster_command = 'dsh -g ' + self.config['dsh_group'] + ' '
        # commit code
        args = ('svn commit --username ' + username + ' --password ' +
                password + ' ' + filename)
        execute(args, "problem with configuration sync")
        # now update on all the nodes in the cluster
        args = (cluster_command + 'svn update --username ' + username +
                ' --password ' + password + ' ' + filename)
        execute(args, "problem with configuration sync")

    def complete_show(self, text, line, begidx, endidx):
        """Tab completion for the show command"""
        if not text:
            completions = self.modules[:]
        else:
            completions = [m for m in self.modules if m.startswith(text)]
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
        if not text:
            if len(line) < 14:
                completions = self.modules[:]
            else:
                completions = []
        else:
            completions = [m for m in self.modules if m.startswith(text)]
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
            filename = self.config[line + '_config']
            #args = ["vi", filename]
            args = "vi " + filename
            log(str(args))
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
        self.prompt = "lvsm(status)# "
        self.modules = ['director', 'firewall', 'virtual', 'real']
        self.director = lvsdirector.Director(self.config['director'],
                                             self.config['maintenance_dir'],
                                             self.config['ipvsadm'])

    def complete_show(self, text, line, begidx, endidx):
        """Tab completion for the show command"""
        protocols = ['tcp', 'udp', 'fwm']
        if line.startswith("show virtual "):
            if line == "show virtual ":
                completions = protocols[:]
            elif len(line) < 16:
                completions = [p for p in protocols if p.startswith(text)]
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
            args = self.config['ipvsadm'] + ' --list'
            execute(args, "problem with ipvsadm", pipe=True)
        elif line == "firewall":
            args = self.config['iptables'] + ' -L -v'
            execute(args, "problem with iptables", pipe=True)
        elif line.startswith("virtual"):
            if len(commands) == 4:
                vip = commands[2]
                if commands[1] == "tcp":
                    protocol = '-t'
                elif commands[1] == "udp":
                    protocol = '-u'
                elif commands[1] == "fwm":
                    protocol = '-f'
                else:
                    print "Usage: virtual tcp|udp|fwm <vip> <port>"
                    return
                port = commands[3]
                args = (self.config['ipvsadm'] + ' --list ' + protocol +
                        ' ' + vip + ':' + str(port))
                try:
                    int(port)
                except ValueError as e:
                    try:
                        portnum = socket.getservbyname(port)
                    except IOError as e:
                        print "[ERROR] " + str(e)
                    else:
                        execute(args, "problem with ipvsadm", pipe=True)
                else:
                    execute(args, "problem with ipvsadm", pipe=True)
            else:
                print self.do_show.__doc__
        elif line.startswith("real"):
            if len(commands) == 3:
                host = commands[1]
                port = commands[2]
                self.director.show_real(host, port)
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

        syntax: disable real|virutal <host> [<port>]
        """
        commands = line.split()
        if len(commands) < 2 or len(commands) > 3:
            print self.do_disable.__doc__
        elif line.startswith("virtual"):
            host = commands[1]
            print "Not implemented yet!"
        elif line.startswith("real"):
            host = commands[1]
            if len(commands) == 2:
                port = ''
            else:
                port = commands[2]
            self.director.disable(host, port)
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

        syntax: enable real|virutal <host>
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
            else:
                port = commands[2]
            self.director.enable(host, port)
        else:
            print self.do_enable.__doc__
