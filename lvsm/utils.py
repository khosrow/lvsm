"""Common utility functions used by lvsm"""
import subprocess
import sys

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


def parse_config(filename):
    #open config file and read it
    lines = print_file(filename)
    # list of valid config keys
    config_items = {'ipvsadm': 'ipvsadm',
                    'iptables': 'iptables',
                    'director_config': '',
                    'firewall_config': '',
                    'dsh_group': '',
                    'director': '',
                    'maintenance_dir': ''
                    }
    linenum = 0
    for line in lines:
        linenum += 1
        if line[0] == '#':
            continue
        k, sep, v = line.rstrip().partition('=')
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
