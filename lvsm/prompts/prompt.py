"""Generic lvsm CommandPrompt"""

import cmd
import logging
import subprocess
import sys
from lvsm import lvs
from lvsm import utils
from lvsm import termcolor


logger = logging.getLogger('lvsm')


class CommandPrompt(cmd.Cmd):
    """
    Generic Class for all command prompts used in lvsm. All prompts should
    inherit from CommandPrompt and not from cmd.Cmd directly.
    """
    settings = {'numeric': False,
                'color': True}
    variables = ['numeric', 'color']
    rawprompt = ''

    def __init__(self, config, stdin=sys.stdin, stdout=sys.stdout):
        # super(CommandPrompt, self).__init__()
        cmd.Cmd.__init__(self)
        self.config = config
        self.director = lvs.Director(self.config['director'],
                                     self.config['maintenance_dir'],
                                     self.config['ipvsadm'],
                                     self.config['director_config'],
                                     self.config['director_cmd'],
                                     self.config['nodes'])
        # disable color if the terminal doesn't support it
        if not sys.stdout.isatty():
            self.settings['color'] = False

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
