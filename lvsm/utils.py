"""Common utility functions used by lvsm"""
import socket
import subprocess
import sys
import logging

logger = logging.getLogger('lvsm')

def parse_config(filename):
    #open config file and read it
    if filename:
        lines = print_file(filename)
    else:
        lines = list()
    # list of valid config keys and their default values
    config_items = {'ipvsadm': 'ipvsadm',
                    'iptables': 'iptables',
                    'pager': '/bin/more',
                    'cache_dir': '/var/cache/lvsm',
                    'template_lang': '',
                    'director_config': '',
                    'parse_director_config': 'yes',
                    'director': 'generic',
                    'director_cmd': '',
                    'director_bin': '',
                    'firewall_config': '',
                    'firewall_cmd': '',
                    'nodes': '',
                    'version_control': '',
                    'git_remote': '',
                    'git_branch': 'master',
                    'keepalived-mib': 'KEEPALIVED-MIB',
                    'snmp_community': '',
                    'snmp_host': '',
                    'snmp_user': '',
                    'snmp_password': ''
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
                if key in ['director_config', 'firewall_config']:
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
        f = open(filename)
        #lines = f.readlines()
        for line in f:
            lines.append(line.rstrip('\n'))
        f.close()
    except IOError as e:
        logger.error(e)
    return lines


def getportnum(port):
    """
    Accepts a port name or number and returns the port number as an int.
    Returns -1 in case of invalid port name.
    """
    try:
        portnum = int(port)
        if portnum < 0 or portnum > 65535:
            logger.error("invalid port number: %s" % port) 
            portnum = -1
    except:
        try:
            p = socket.getservbyname(port)
            portnum = int(p)
        except socket.error, e:
            logger.error("%s: %s" % (e, port))
            portnum = -1
    return portnum


def gethostbyname_ex(host):
    """Accepts a hostname and return it's IPv4 address(es) as a list"""
    try:
        (hostname, aliaslist, ipaddrlist) = socket.gethostbyname_ex(host)
    except socket.gaierror as e:
        logger.error("%s: %s" % (e.strerror, host))
        return list()
    else:
        return ipaddrlist


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


def check_output(args, cwd=None, silent=False):
    """Wrapper for subprocess.check_output"""
    if not silent:
        logger.info("Running command: %s " % " ".join(args))
    try:
        try:
            output = subprocess.check_output(args, cwd=cwd)
            return output
        # python 2.6 compatibility code
        except AttributeError:
            output, stderr = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=cwd).communicate()
            return output
    except OSError as e:
        logger.error(e)
