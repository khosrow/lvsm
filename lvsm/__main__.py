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
  -m, --monochrome      Disable color display
  -n, --numeric         Enable numeric host names, and avoid using DNS
  -v, --version         Display lvsm version
"""

import getopt
import sys
import __init__ as appinfo
import logging
import os

from lvsm import utils
from lvsm import shell

logging.basicConfig(format='[%(levelname)s]: %(message)s')
logger = logging.getLogger('lvsm')  

def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__

    config = utils.parse_config(None)
    lvsshell = shell.LivePrompt(config)
    lvsshell.onecmd(' '.join(["help"]))
    print >> fd, "Use 'lvsm help <command>' for information on a specific command."

    if msg:
        print >> fd, msg
    sys.exit(code)


def main():
    CONFFILE = "/etc/lvsm.conf"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvc:dmn",
                                   ["help", "version", "config=", "debug", "monochrome", "numeric"])
    except getopt.error, msg:
        usage(2, msg)

    color = True
    numeric = False
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
        elif opt in ("-m", "--monochrome"):
            color = False
        elif opt in ("-n", "--numeric"):
            numeric = True

    # open config file and read it
    # config = utils.parse_config(CONFFILE)
    config = utils.parse_config(os.path.expanduser(os.path.expandvars(CONFFILE)))
    logger.debug('Parsed config file')
    logger.debug(str(config))

    try:
        lvsshell = shell.LivePrompt(config)

        if not color:
            lvsshell.do_set("color off")
        if numeric:
            lvsshell.do_set("numeric on")

        if args:
            lvsshell.onecmd(' '.join(args[:]))
        else:
            lvsshell.cmdloop()
    except KeyboardInterrupt:
        print "\nleaving abruptly!"
        sys.exit(1)

if __name__ == "__main__":
    main()
