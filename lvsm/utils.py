"""Common utility functions used by lvsm"""
import socket
import struct
import subprocess
import sys
import logging

logger = logging.getLogger('lvsm')

def parse_config(filename):
    #open config file and read it
    lines = print_file(filename)
    # list of valid config keys and their default values
    config_items = {'ipvsadm': 'ipvsadm',
                    'iptables': 'iptables',
                    'pager': '/bin/more',
                    'director_config': '',
                    'firewall_config': '',
                    'director': 'generic',
                    'director_cmd': '',
                    'director_bin': '',
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
                logger.error("configuration file line %d: invalid variable '%s'"  % (linenum, key))
                sys.exit(1)
            else:
                config_items[key] = value
                # if the item is a config file, verify that the file exists
                if key.endswith('_config'):
                    try:
                        file = open(value)
                        file.close()
                    except IOError as e:
                        logger.error("in lvsm configuration file line %d" % linenum)
                        logger.error(e)
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
        logger.error(e)
    return lines


def getportnum(port):
    """accepts a port name or number and returns the port number as an int.
except
    returns -1 in case of invalid port name"""
    try:
        portnum = int(port)
        if portnum < 0 or portnum > 65535:
            logger.error("invalid port number")
            portnum = -1
    except:
        try:
            p = socket.getservbyname(port)
            portnum = int(p)
        except socket.error, e:
            logger.error(e)
            portnum = -1
    return portnum


def gethostname(host):
    try:
        hostip = socket.gethostbyname(host)
    except socket.gaierror as e:
        logger.error(e.strerror)
        return ''
    else:
        return hostip


def hextoip(hexip):
    """Convert a hex format IPv4 to a dotted notation"""
    ip = int(hexip, 16)
    return socket.inet_ntoa(struct.pack("!L",ip))


def pager(pager,lines):
    """print lines to screen and mimic behaviour of MORE command"""
    text = "\n".join(lines)
    if pager.upper() == 'NONE':
        print text
    else:
        try:
            p = subprocess.Popen(pager.split(), stdin=subprocess.PIPE)
        except OSError as e:
            logger.error("Problem with pager: %s" % pager)
            logger.error(e)
        else:
            stdout, stderr = p.communicate(input=text)


def check_output(args):
    """Wrapper for subprocess.check_output"""
    logger.debug("Running: %s " % " ".join(args))
    try:
        output = subprocess.check_output(args)
        return output
    # python 2.6 compatibility code
    except AttributeError:
        output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
        return output
