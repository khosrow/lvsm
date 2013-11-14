import getpass
import subprocess
import sys
import shutil
import tempfile
import utils
import termcolor
import logging

from prompt import CommandPrompt


logger = logging.getLogger('lvsm')


class ConfigurePrompt(CommandPrompt):
    """
    Configure prompt class. Handles commands for manipulating configuration
    items in the various plugins.
    """
    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        CommandPrompt.__init__(self, config)
        # List of moduels used in autocomplete function
        self.modules = ['director', 'firewall']
        self.rawprompt = "lvsm(configure)# "
        # Setup color related things here
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
