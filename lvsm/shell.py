"""Generic lvsm CommandPrompt"""

import cmd
import getpass
import logging
import shutil
import subprocess
import sys
import tempfile

from lvsm import lvs
from lvsm import utils
from lvsm import termcolor
from lvsm import firewall


# from lvsm.prompts import configure, virtual, real, prompt


logger = logging.getLogger('lvsm')


class CommandPrompt(cmd.Cmd):
    """
    Generic Class for all command prompts used in lvsm. All prompts should
    inherit from CommandPrompt and not from cmd.Cmd directly.
    """
    settings = {'numeric': False,
                'color': True}
    variables = ['numeric', 'color']

    def __init__(self, config, rawprompt='', stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        cmd.Cmd.__init__(self)
        self.config = config
        self.director = lvs.Director(self.config['director'],
                                     self.config['ipvsadm'],
                                     self.config['director_config'],
                                     self.config['director_cmd'],
                                     self.config['nodes'])
        
        self.rawprompt = rawprompt
        # disable color if the terminal doesn't support it
        if not sys.stdout.isatty():
            self.settings['color'] = False

        if self.settings['color']:
            c = "red"
            a = ["bold"]
        else:
            c = None
            a = None
        self.prompt = termcolor.colored(self.rawprompt, color=c,
                                        attrs=a)    

    def emptyline(self):
        """Override the default emptyline and return a blank line."""
        pass

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        # check to see if the prompt should be colorized
        if self.settings['color']:
            self.prompt = termcolor.colored(self.rawprompt, #attrs=None)
                                            color="red", attrs=["bold"])
        else:
            self.prompt = self.rawprompt
        return stop

    def do_exit(self, line):
        """Exit from lvsm shell."""
        modified = list()
        if self.config['version_control'] == 'svn':
            # check to see if any config files are modified using "svn status"
            # the command will return 'M  filename' if a file is modified
            args = ["svn", "status"]

            if self.config['director_config']:
                args.append(self.config['director_config'])
                logger.debug('Running command : %s' % (' '.join(args)))
                try:
                    result = utils.check_output(args)
                except OSError as e:
                    print"[ERROR]: " + e.strerror
                except subprocess.CalledProcessError as e:
                    print"[ERROR]: " + e.output
                if result and result[0] == "M":
                    modified.append(self.config['director_config'])

            if self.config['firewall_config']:
                args.append(self.config['firewall_config'])
                try:
                    try:
                        result = subprocess.check_output(args)
                    except AttributeError as e:
                        result, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
                except OSError as e:
                    print("[ERROR]: " + e.strerror)
                if result and result[0] == "M":
                    modified.append(self.config['firewall_config'])

            if modified:
                print "The following config file(s) were not comitted to svn:"
                for filename in modified:
                    print filename
                print
                while True:
                    answer = raw_input("Do you want to quit? (y/n) ")
                    if answer.lower() == "y":
                        print "goodbye."
                        sys.exit(0)
                    elif answer.lower() == "n":
                        break

        if not modified:
            print "goodbye."
            sys.exit(0)

    def do_quit(self, line):
        """Exit from lvsm shell."""
        self.do_exit(line)

    def do_end(self, line):
        """Return to previous context."""
        return True

    def do_set(self, line):
        """Set or display different variables."""
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
                        print "syntax: set numeric on|off"
                elif tokens[0] == "color":
                    if tokens[1] == "on":
                        self.settings['color'] = True
                        self.prompt = termcolor.colored(self.rawprompt,
                                                        color="red",
                                                        attrs=["bold"])
                    elif tokens[1] == "off":
                        self.settings['color'] = False
                        self.prompt = self.rawprompt
                    else:
                        print "syntax: set color on|off"
                else:
                    self.help_set()
            else:
                self.help_set()

    def help_help(self):
        print
        print "show help"

    def help_set(self):
        print "Set or display different variables."
        print ""
        print "syntax: set [<variable>] [<value>]"
        print ""
        print "<variable> can be one of:"
        print "\tnumeric on|off          Toggle numeric ipvsadm display ON/OFF"
        print "\tcolor on|off            Toggle color display ON/OFF"
        print ""

    def complete_set(self, text, line, begidx, endidx):
        """Tab completion for the set command."""
        if len(line) < 12:
            if not text:
                    completions = self.variables[:]
            else:
                completions = [m for m in self.variables if m.startswith(text)]
        else:
            completions = []
        return completions


class LivePrompt(CommandPrompt):
    """
    Class for the live command prompt. This is the main landing point
    and is called from __main__.py
    """
    def __init__(self, config, rawprompt='', stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        CommandPrompt.__init__(self, config, rawprompt="lvsm(live)# ")
        self.modules = ['director', 'firewall', 'nat', 'virtual', 'real']
        self.protocols = ['tcp', 'udp', 'fwm']
        self.firewall = firewall.Firewall(self.config['iptables'])

    def do_configure(self, line):
        """Enter configuration level."""
        commands = line.split()
        # configshell = prompts.configure.ConfigurePrompt(self.config)
        configshell = ConfigurePrompt(self.config)
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

        from lvsm.modules import ldirectordprompts
        from lvsm.modules import keepalivedprompts
        prompts = {'generic': VirtualPrompt,
                   'ldirectord': ldirectordprompts.VirtualPrompt,
                   'keepalived': keepalivedprompts.VirtualPrompt}

        virtualshell = prompts[self.config['director']](self.config)

        if not line:
            virtualshell.cmdloop()
        else:
            virtualshell.onecmd(' '.join(commands[0:]))

    # def do_real(self,line):
    #     """
    #     \rReal Server level.
    #     \rLevel providing information on real servers
    #     """
    #     commands = line.split()
    #     # realshell = prompts.real.RealPrompt(self.config)
    #     realshell = RealPrompt(self.config)
    #     if not line:
    #         realshell.cmdloop()
    #     else:
    #         realshell.onecmd(' '.join(commands[0:]))

    def do_firewall(self, line):
        """
        \rFirewall level.
        \riptables information is available at this level.
        """
        commands = line.split()

        fwshell = FirewallPrompt(self.config)
        if not line:
            fwshell.cmdloop()
        else:
            fwshell.onecmd(' '.join(commands[0:]))

    def do_restart(self, line):
        """Restart the direcotr or firewall module."""
        if line == "director":
            if self.config['director_cmd']:
                print "restaring director"
                try:
                    subprocess.call(self.config['director_cmd'], shell=True)
                except OSError as e:
                    logger.error("problem while restaring director - %s" % e.strerror)
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

    def do_version(self, line):
        """
        \rDisplay version information about modules
        """
        pager = self.config['pager']
        args = [self.config['ipvsadm'], '--version']
        output = list()
        ipvsadm = utils.check_output(args)
        header = ["", "Linux Virtual Server",
                  "===================="]

        output += header
        output.append(ipvsadm)
        output.append("")

        if not self.config['director_bin'] :
            director =  'director binary not defined. Unable to get version!'
        else:
            args = [self.config['director_bin'], '--version']
            director = utils.check_output(args).split('\n')[0]

        header = ["Director",
                  "========"]

        output += header
        output.append(director)
        output.append("")

        args = [self.config['iptables'], '--version']
        iptables = utils.check_output(args)
        header = ["Packet Filtering",
                  "================"]

        output += header
        output.append(iptables)
        output.append("")

        utils.pager(pager, output)

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


class ConfigurePrompt(CommandPrompt):
    """
    Configure prompt class. Handles commands for manipulating configuration
    items in the various plugins.
    """
    def __init__(self, config, rawprompt='', stdin=sys.stdin, stdout=sys.stdout):
        CommandPrompt.__init__(self, config, rawprompt="lvsm(configure)# ")
        # List of moduels used in autocomplete function
        self.modules = ['director', 'firewall']

    def svn_sync(self, filename, username, password):
        """Commit changed configs to svn and do update on remote node."""
        # commit config locally
        args = ['svn',
                'commit',
                '--username',
                username,
                '--password',
                password,
                filename]
        svn_cmd = ('svn commit --username ' + username +
                   ' --password ' + password + ' ' + filename)
        logger.debug('Running command : %s' % svn_cmd)
        try:
            result = subprocess.call(svn_cmd, shell=True)
        except OSError as e:
            logger.error("Problem with configuration sync - %s" % e.strerror)

        # update config on all nodes
        n = self.config['nodes']
        if n != '':
            nodes = n.replace(' ', '').split(',')
        else:
            nodes = None

        try:
            hostname = utils.check_output(['hostname', '-s'])
        except (OSError, subprocess.CalledProcessError):
            hostname = ''
        if nodes is not None:
            svn_cmd = ('svn update --username ' + username +
                       ' --password ' + password + ' ' + filename)
            for node in nodes:
                if node != hostname:
                    args = 'ssh ' + node + ' ' + svn_cmd
                    logger.debug('Running command : %s' % (' '.join(args)))
                    try:
                        subprocess.call(args, shell=True)
                    except OSError as e:
                        logger.error("Problem with configuration sync - %s" % e.strerror)

    def complete_show(self, text, line, begidx, endidx):
        """Tab completion for the show command."""
        if len(line) < 14:
            if not text:
                completions = self.modules[:]
            else:
                completions = [m for m in self.modules if m.startswith(text)]
        else:
            completions = []
        return completions

    def help_show(self):
        ""
        print "Show configuration for an item. The configuration files are defined in lvsm.conf"
        print ""
        print "<module> can be one of the following"
        print "\tdirector                the IPVS director config file"
        print "\tfirewall                the iptables firewall config file"
        print ""

    def do_show(self, line):
        """Show director or firewall configuration."""
        if line == "director" or line == "firewall":
            configkey = line + "_config"
            if not self.config[configkey]:
                logger.error("'%s' not defined in configuration file!" % configkey)
            else:
                lines = utils.print_file(self.config[configkey])
                utils.pager(self.config['pager'], lines)
        else:
            print "\nsyntax: show <module>\n"

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

    def help_edit(self):
        print ""
        print "Edit the configuration of an item. The configuration files are defined in lvsm.conf"
        print "syntax: edit <module>"
        print ""
        print "<module> can be one of the follwoing"
        print "\tdirector                the IPVS director config file"
        print "\tfirewall                the iptables firewall config file"
        print ""

    def do_edit(self, line):
        """Edit the configuration of an item."""
        if line == "director":
            key = line + "_config"
            filename = self.config[key]
            if not filename:
                logger.error("'%s' not defined in config file!" % key)
            else:
                # make a temp copy of the config
                try:
                    temp = tempfile.NamedTemporaryFile()
                    shutil.copyfile(filename, temp.name)
                except IOError as e:
                    logger.error(e.strerror)

                while True:
                    args = "vi " + temp.name
                    logger.debug('Running command : %s' % args)
                    result = subprocess.call(args, shell=True)
                    if result != 0:
                        logger.error("Something happened during the edit of %s" % self.config[key])
                    # Parse the config file and verify the changes
                    # If successful, copy changes back to original file
                    if self.director.parse_config(temp.name):
                        shutil.copyfile(temp.name, filename)
                        temp.close()
                        break
                    else:
                        answer = raw_input("You had a syntax error in your config file, edit again? (y/n) ")
                        if answer.lower() == 'y':
                            pass
                        elif answer.lower() == 'n':
                            logger.warn("Changes were not saved due to syntax errors.")
                            break

        elif line == "firewall":
            key = line + "_config"
            filename = self.config[key]
            if not filename:
                logger.error("'%s' not defined in config file!" % key)
            else:
                args = "vi " + filename
                logger.debug(str(args))
                result = subprocess.call(args, shell=True)
                if result != 0:
                    logger.error("Something happened during the edit of %s" % self.config[key])
        else:
            print "syntax: edit <module>"

    def help_sync(self):
        print "Sync all configuration files across the cluster."
        print ""
        print "syntax: sync"

    def do_sync(self, line):
        """Sync all configuration files across the cluster."""
        if line:
            print "syntax: sync"
        elif self.config['version_control'] == 'svn':
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
        else:
            print "You need to define version_control in lvsm.conf"
"""Various levels of command line shells for accessing ipvs and iptables
functionality form one location."""


class VirtualPrompt(CommandPrompt):
    def __init__(self, config, rawprompt='', stdin=sys.stdin, stdout=sys.stdout):
        # Change the word delimiters so that - or . don't cause a new match
        try:
            import readline
            readline.set_completer_delims(' ')
        except ImportError:
            pass
        # super(CommandPrompt, self).__init__()
        CommandPrompt.__init__(self, config, rawprompt="lvsm(live)(virtual)# ")
        self.modules = ['director', 'firewall', 'nat', 'virtual', 'real']
        self.protocols = ['tcp', 'udp', 'fwm']
        self.firewall = firewall.Firewall(self.config['iptables'])

    def do_status(self,line):
        """
        \rDisplay status of all virtual servers
        """
        syntax = "\nstatus\n"
        numeric = self.settings['numeric']
        color = self.settings['color']

        if not line:
            d = self.director.show(numeric, color)
            d.append('')
            # f = self.firewall.show(numeric, color)
            # utils.pager(self.config['pager'], d + f)
            utils.pager(self.config['pager'], d)
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

    def do_disable(self, line):
        """
        \rDisable real server across VIPs.
        \rsyntax: disable <rip> <port>
        """

        syntax = "syntax: disable <rip> <port>"

        commands = line.split()
        if len(commands) > 2 or len(commands) == 0:
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
        """
        \rEnable real server across VIPs.
        \rsyntax: enable <rip> <port>
        """

        syntax = "syntax: enable <rip> <port>"

        commands = line.split()
        if len(commands) > 2 or len(commands) == 0:
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
            if not self.director.enable(host, port):
                logger.error("Could not enable %s" % host)
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

# class RealPrompt(CommandPrompt):
#     def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
#         # super(CommandPrompt, self).__init__()
#         CommandPrompt.__init__(self, config)
#         self.modules = ['director', 'firewall', 'nat', 'virtual', 'real']
#         self.protocols = ['tcp', 'udp', 'fwm']
#         self.firewall = firewall.Firewall(self.config['iptables'])
#         self.rawprompt = "lvsm(live)(real)# "
#         if self.settings['color']:
#             c = "red"
#             # c = None
#             a = ["bold"]
#             # a = None
#         else:
#             c = None
#             a = None
#         self.prompt = termcolor.colored(self.rawprompt, color=c,
#                                         attrs=a)

#     def do_show(self, line):
#         """Show information about a specific real server."""
#         syntax = "\nsyntax: show <server> <port>\n"
#         commands = line.split()
#         numeric = self.settings['numeric']
#         color = self.settings['color']
#         if len(commands) == 2:
#             host = commands[0]
#             port = commands[1]
#             utils.pager(self.config['pager'], self.director.show_real(host, port, numeric, color))
#         else:
#             print syntax

#     def do_disable(self, line):
#         """Disable a real or virtual server."""
#         syntax = "\nsyntax: disable <host> [<port>]\n"
#         commands = line.split()
#         if len(commands) > 2:
#             print syntax
#         elif len(commands) <= 2:
#             host = commands[0]
#             if len(commands) == 1:
#                 port = ''
#             elif len(commands) == 2:
#                 port = commands[1]
#             else:
#                 print syntax
#                 return
#             # ask for an optional reason for disabling
#             reason = raw_input("Reason for disabling [default = None]: ")
#             if not self.director.disable(host, port, reason):
#                 logger.error("Could not disable %s" % host)
#         else:
#             print syntax

#     def do_enable(self, line):
#         """Enable a real or virtual server."""
#         syntax = "\nsyntax: enable <host> [<port>]\n"
#         commands = line.split()
#         if len(commands) > 2:
#             print syntax
#         elif len(commands) <= 2:
#             host = commands[0]
#             if len(commands) == 1:
#                 port = ''
#             elif len(commands) == 2:
#                 port = commands[0]
#             else:
#                 print syntax
#                 return
#             if not self.director.enable(host, port):
#                 logger.error("Could not enable %s" % host)
#         else:
#             print syntax

#     def help_show(self):
#         print ""
#         print "Show information about a specific real server."
#         print "syntax: show <server> <port>"
#         print ""

#     def help_disable(self):
#         print ""
#         print "Disable a real server."
#         print "syntax: disable <host> [<port>]"
#         print ""

#     def help_enable(self):
#         print ""
#         print "Enable a real server."
#         print "syntax: enable <host> [<port>]"
#         print ""

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

class FirewallPrompt(CommandPrompt):
    """Class handling shell prompt for firewall (iptables) related actions"""
    def __init__(self, config, rawprompt='', stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        CommandPrompt.__init__(self, config, rawprompt="lvsm(live)(firewall)# ")
        self.firewall = firewall.Firewall(self.config['iptables'])

    def do_status(self, line):
        """
        \rDisplay status of all packet filtering rules
        """
        ports = self.firewall.show(self.settings['numeric'], self.settings['color'])
        nat = self.firewall.show_nat(self.settings['numeric'])

        utils.pager(self.config['pager'], ports + nat + [''])

    def do_show(self, line):
        """
        \rShow the NAT table or the packet filter table
        \rsyntax: show nat|filters
        """
        if line == "nat":
            output = self.firewall.show_nat(self.settings['numeric'])
        elif line == "filters":
            output = self.firewall.show(self.settings['numeric'], self.settings['color'])
        else:
            print "\nsyntax: show nat|filters"
            return
        utils.pager(self.config['pager'], output + [''])

    def complete_show(self, text, line, begidx, endidx):
        """Command completion for the show command"""
        args = ['nat', 'filters']
        if not text:
            completions = args[:]
        else:
            completions = [s for s in args if s.startswith(text)]
        return completions