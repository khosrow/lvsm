"""Common utility functions used by lvsm"""
import socket
import subprocess
import sys
import termcolor
import subprocess
from getch import getch


DEBUG = False
ROWS = 24
COLS = 85


def log(msg):
    if DEBUG:
        print "[DEBUG] " + msg


def parse_config(filename):
    #open config file and read it
    lines = print_file(filename)
    # list of valid config keys and their default values
    config_items = {'ipvsadm': 'ipvsadm',
                    'iptables': 'iptables',
                    'director_config': '',
                    'firewall_config': '',
                    'director': '',
                    'maintenance_dir': '',
                    'director_cmd': '',
                    'firewall_cmd': '',
                    'nodes': '',
                    'version_control': ''
                    }
    linenum = 0
    for line in lines:
        linenum += 1
        conf, sep, comment = line.rstrip().partition('#')
        if conf:
            k, sep, v = conf.rstrip().partition('=')
            key = k.lstrip().rstrip()
            value = v.lstrip().rstrip()
            if config_items.get(key) is None:
                print "[ERROR] configuration file line " + str(linenum) +\
                      ": invalid variable '" + key + "'"
                sys.exit(1)
            else:
                config_items[key] = value
                # if the item is a config file, verify that the file exists
                if key.endswith('_config'):
                    try:
                        file = open(value)
                        file.close()
                    except IOError as e:
                        print "[ERROR] in lvsm configuration file line " +\
                              str(linenum)
                        print "[ERROR] " + e.strerror + ": '" + e.filename +\
                              "'"
                        sys.exit(1)
    return config_items


def print_file(filename):
    """opens a file and returns its contents as list"""
    lines = list()
    try:
        file = open(filename)
        lines = file.readlines()
        file.close()
    except IOError as e:
        print "[ERROR] Unable to read '" + e.filename + "'"
        print "[ERROR] " + e.strerror + ": '" + e.filename + "'"
    return lines


def getportnum(port):
    """accepts a port name or number and returns the port number as an int.
    returns -1 in case of invalid port name"""
    try:
        portnum = int(port)
        if portnum < 0 or portnum > 65535:
            print "[ERROR] invalid port number"
            portnum = -1
    except:
        try:
            p = socket.getservbyname(port)
            portnum = int(p)
        except socket.error, e:
            print "[ERROR] " + str(e)
            portnum = -1
    return portnum


def gethostname(host):
    try:
        hostip = socket.gethostbyname(host)
    except socket.gaierror as e:
        print "[ERROR] " + e.strerror
        return ''
    else:
        return hostip


def pager(lines):
    """print lines to screen and mimic behaviour of MORE command"""
    global ROWS
    i = 0
    if lines is not None:
        for line in lines:
            i = i + 1
            if ROWS and i == int(ROWS):
                more = termcolor.colored("-- More --", color=None,
                                         attrs=["reverse"])
                print more + "\r",
                ch = getch()
                # erase the "-- More --"
                print "          \r",
                # pressing 'q' will go back to prompt
                # pressing 'enter' will advance by 1 line
                # otherwise show next page
                if ord(ch) == 113:
                    return
                elif ord(ch) == 13:
                    i = i - 1
                else:
                    i = 0
            print line.rstrip()


def sigwinch_handler(signum, frame):
    update_rows_cols()


def update_rows_cols():
    global ROWS, COLS
    args = ["/bin/stty", "size"]
    try:
        s = check_output(args)
    except (OSError, subprocess.CalledProcessError) as e:
        ROWS = 1000
    else:
        ROWS, COLS = s.split()


def check_output(args):
    """Wrapper for subprocess.check_output"""
    try:
        output = subprocess.check_output(args)
        return output
    # python 2.6 compatibility code
    except AttributeError as e:
        output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        return output
