#!/usr/bin/env python
# Khosrow Ebrahimpour - Sep 2012

"""
lvsm - LVS Manager
LVS Manager is a shell that eases the management of a linux virtual server.

Using it without arguments will enter an interactive shell. Supplying one or
more command-line arguments will run lvsm for a "single-shot" use.

Usage: lvsm [-h] [-c <conffile>][commands]

Options:
  -h, --help            Show this help message and exit
  -c <conffile>, -config=<connfile>         
                        Specify which configuration file to use
                        The default is /etc/lvsm.conf
  -d, --debug           Enable debug messages during runtime
  -v, --version         Display lvsm version

Commands:
  configure
  status
  help

Use 'lvsm help <command>' for information on a specific command.
"""

import getopt
import sys
import __init__ as appinfo
import prompts.live
import utils
import logging


def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__
    if msg:
        print >> fd, msg
    sys.exit(code)


def main():
    CONFFILE = "/etc/lvsm.conf"
    logging.basicConfig(format='[%(levelname)s]: %(message)s')
    logger = logging.getLogger('lvsm')  

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvc:d",
                                   ["help", "version", "config=", "debug"])
    except getopt.error, msg:
        usage(2, msg)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(0)
        elif opt in ("-v", "--version"):
            print "lvsm " + appinfo.__version__
            sys.exit(0)
        elif opt in ("-c", "--config"):
            CONFFILE = arg
        elif opt in ("-d", "--debug"):
            logger.setLevel(logging.DEBUG)

    # open config file and read it
    config = utils.parse_config(CONFFILE)
    logger.debug('Parsed config file')
    logger.debug(str(config))

    try:
        shell = prompts.live.LivePrompt(config)
        if args:
            shell.onecmd(' '.join(args[:]))
        else:
            shell.cmdloop()
    except KeyboardInterrupt:
        print "\nleaving abruptly!"
        sys.exit(1)

if __name__ == "__main__":
    main()
