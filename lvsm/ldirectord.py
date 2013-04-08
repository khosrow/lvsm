
import os
import re
import socket
import subprocess
import sys
import time
import utils
from genericdirector import GenericDirector

class Ldirectord(GenericDirector):
    """Handles ldirector-specific functionality like enable/disable actions.
    """
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        super(Ldirectord, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd, nodes)

    def disable(self, host, port='', reason=''):
        # Prepare a canned error message
        error_msg = "[ERROR] problem disabling on remote node - "
        if self.maintenance_dir:
            hostip = utils.gethostname(host)
            if not hostip:
                return False
            if port:
                # check that it's a valid port
                portnum = utils.getportnum(port)
                if portnum == -1:
                    return False
                hostport = hostip + ":" + str(portnum)
            else:
                hostport = hostip
            # go through maint_dir to see if host is already disabled
            filenames = os.listdir(self.maintenance_dir)
            for filename in filenames:
                f = self.convert_filename(filename)
                if hostport == f or hostip == f:
                    print "host is already disabled!"
                    return True
            try:
                f = open(self.maintenance_dir + "/" + hostport, 'w')
                f.write(reason)
            except IOError as e:
                print "[ERROR] " + e.strerror + ": '" + e.filename +\
                      "'"
                return False

            if self.nodes is not None:
                filename = self.maintenance_dir + "/" + hostport
                for node in self.nodes:
                    if node != self.hostname:
                        remote = node + ":" + self.maintenance_dir
                        args = ['scp', filename, remote]
                        try:
                            output = utils.check_output(args)
                        except OSError as e:
                            print error_msg + e.strerror
                        except subprocess.CalledProcessError as e:
                            print error_msg + e.output
            # now confirm that it's removed from ldirector
            i = 0
            print "Disabling server ",
            while i < 3:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(1.5)
                i = i + 1
            output = self.show_running(numeric=True, color=False)
            for line in output:
                if hostport in line:
                    print " Failed"
                    # note: even if the real is still showing up, we've created
                    # the file, so we should still return true
                    return True
            print " OK"
            return True
        else:
            print "[ERROR] maintenance_dir not defined in config."
            return False

    def enable(self, host, port=''):
        """enable a previously disabled server"""
        # Prepare a canned error message.
        error_msg = "[ERROR] problem enabling on remote node - "
        hostip = utils.gethostname(host)
        if not hostip:
            return False
        # If port was provided the file will be of form xx.xx.xx.xx:nn
        if port:
            # Check that the port is valid.
            portnum = utils.getportnum(port)
            if portnum == -1:
                return False
            hostport = hostip + ":" + str(portnum)
        # If no port was provided the file be of form xx.xx.xx.xx
        else:
            hostport = hostip
        if self.maintenance_dir:
            filenames = os.listdir(self.maintenance_dir)
            # Go through all files in maintenance_dir
            # and find a matching filename, and remove it.
            for filename in filenames:
                f = self.convert_filename(filename)
                # If user asks to enable xx.xx.xx.xx and xx.xx.xx.xx:nn
                # is disabled, we enable all ports and remove all the files.
                if (hostport == f or (not port and hostip in f)):
                    try:
                        os.unlink(self.maintenance_dir + "/" + filename)
                    except OSError as e:
                        print "[ERROR] " + e.strerror + ": '" +\
                              e.filename + "'"
                        return False
                    # Remove the same file from other nodes in the cluster.
                    if self.nodes is not None:
                        for node in self.nodes:
                            if node != self.hostname:
                                cmd = "rm " + self.maintenance_dir + "/" + filename
                                args = ['ssh', node, cmd]
                                try:
                                    output = utils.check_output(args)
                                except OSError as e:
                                    print error_msg + e.strerror
                                except subprocess.CalledProcessError as e:
                                    print error_msg + e.output
                    # Wait 4.5 seconds before checking output of ipvsadm.
                    i = 0
                    print "Enabling server ",
                    while i < 3:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        time.sleep(1.5)
                        i = i + 1

                    # Verify that the host is active in ldirectord.
                    output = self.show_running(numeric=True, color=False)
                    for line in output:
                        if hostport in line:
                            print " OK"
                            return True
                    # If we get to this point, means the host is not active.
                    print " Failed"
                    # Note: even if the real isn't showing up, we have removed
                    # the file, so we should still return true.
                    return True
            # If we make it out here means the real wasn't in the file list.
            print "[ERROR] Server not found in maintenance_dir!"
            return False
        else:
            print "[ERROR] maintenance_dir not defined!"
            return False

    def show_real_disabled(self, host, port, numeric):
        """show status of disabled real server across multiple VIPs"""
        # note that host='' and port='' returns all disabled server
        if host and port:
            hostip = utils.gethostname(host)
            if not hostip:
                return
            portnum = utils.getportnum(port)
            if portnum == -1:
                return
            hostport = hostip + ":" + str(portnum)
        # output = ["", "Disabled servers:", "-----------------"]
        output = list()
        filenames = os.listdir(self.maintenance_dir)
        for filename in filenames:
            try:
                f = open(self.maintenance_dir + "/" + filename)
                reason = 'Reason: ' + f.readline()
            except IOError as e:
                reason = ''
                print "[ERROR] " + e.strerror + ' \'' + e.filename + '\''
            if ((not host and not port) or
                self.convert_filename(filename) == hostip or
                self.convert_filename(filename) == hostip + ":" +
                str(portnum)):
                # decide if we have to convert to hostname or not
                if numeric:
                    output.append(filename + "\t\t" + reason)
                else:
                    rip = filename.split(":")[0]
                    try:
                        (ripname, al, ipl) = socket.gethostbyaddr(rip)
                    except socket.herror, e:
                        print "[ERROR] " + str(e)
                        return False
                    if len(filename.split(":")) == 2:
                        ripport = filename.split(":")[1]
                        ripportname = socket.getservbyport(int(ripport))
                        ripname = ripname + ':' + ripportname
                    else:
                        pass
                    output.append(ripname + "\t\t" + reason)
        return output

    def parse_config(self, configfile):
        """Read the config file and validate each line"""
        try:
            f = open(configfile)
        except IOError as e:
            print "[ERROR] " + e.strerror
            return False

        in_vip = False
        counter = 0
        
        for line in f:
            counter = counter + 1
            # Remove comment lines and empty lines
            (text, sep, comment) = line.partition('#')
            if text.strip() == '':
                continue
            else:
                line = text.rstrip()
                # print line
            (k, sep, v) = text.partition("=")
            keyword = k.rstrip()
            value = v.lstrip().rstrip()
            # If we are in a virtual section, parse the input accordingly.
            if in_vip:
                # Replace tabs with 4 spaces
                line = re.sub("\t", "    ", line)

                # If a line begins with 4 spaces process it
                m_re = re.search("^ {4,}(.+)", line)
                if m_re is not None:
                    text = m_re.group(1)
                    if not self.parse_virtual(text, counter, af_inet6):
                        return False
                else:
                    # A new line without spaces means we exited the virtual section
                    in_vip = False
            
            if not in_vip:
                if keyword == "virtual" or keyword == "virtual6":
                    # Set a flag that all subsequent config items are part of a VIP
                    in_vip = True

                    # Check address family of the VIP
                    if keyword == "virtual":
                        af_inet6 = None
                    else:
                        af_inet6 = 6

                    ipport = value
                    # Perform regexp matches to get the ip/port
                    ip4_re = re.search("^(\d+\.\d+\.\d+\.\d+):([0-9a-zA-Z-_]+)", ipport)
                    host_re = re.search("^([0-9a-zA-Z._+-]+):([0-9a-zA-Z-_]+)", ipport)
                    ip6_re = re.search("^\[([0-9A-Fa-f:]+)\]:([0-9a-zA-Z-_]+)", ipport)
                    fwm_re = re.search("^(\d+)", ipport)

                    # Verify the IPv4 address and port are correct
                    if ip4_re is not None and af_inet6 is None:
                        ip_port = ip4_re.group(1) + ":" + ip4_re.group(2)
                        virtual_port = ip4_re.group(2)
                    # If hostname is given
                    elif host_re is not None:
                        ip_port = host_re.group(1) + ":" + host_re.group(2)
                        virtual_port = host_re.group(2)
                    # If IPv6 address was given verify
                    elif ip6_re is not None and af_inet6 is None:
                        print "[PARSE ERROR] Line: " + str(counter) + " - Cannot specify IPv6 address with virtual="
                        print line
                        return False
                    elif ip6_re is not None and af_inet6 is not None:
                        # TODO: code to ensure ipv6 addr is in the right range
                        ip_port = "[" + ip6_re.group(1) + "]:" + ip6_re.group(2)
                        virtual_port = ip6_re.group(2)
                    # If fwm was defined
                    elif fwm_re is not None:
                        fwm = fwm_re.group(1)
                    else:
                        print "[PARSE ERROR] Line: " + str(counter) + "  - Invalid address for virtual server."
                        print line
                elif keyword == "checktimeout" and value.isdigit():
                    pass
                elif keyword == "negotiatetimeout" and value.isdigit():
                    pass
                elif keyword == "checkinterval" and value.isdigit():
                    pass
                elif keyword == "failurecount" and value.isdigit():
                    pass
                elif keyword == "fallback":
                    #do some checks to make sure IPv4 is active
                    pass
                elif keyword == "fallback6":
                    # do checks to make sure IPv6 is active
                    pass
                elif keyword == "fallbackcommand":
                    pass
                elif keyword == "autoreload" and value in ('yes', 'no'):
                    pass
                elif keyword == "callback" and utils.has_quotes(value):
                    pass
                elif keyword == "logfile" and utils.has_quotes(value):
                    pass
                elif keyword == "execute":
                    pass
                elif keyword == "fork" and value in ('yes', 'no'):
                    pass
                elif keyword == "supervised" and value in ('yes', 'no'):
                    pass
                elif keyword == "quiescent" and value in ('yes', 'no'):
                    pass
                elif keyword == "readdquiescent" and value in ('yes', 'no'):
                    pass
                elif keyword == "emailalert":
                    # verify email address format
                    pass
                elif keyword == "emailalertfreq" and value.isdigit():
                    pass
                elif keyword == "emailalertstatus":
                    pass
                elif keyword == "emailalertfrom":
                    # verify email address
                    pass
                elif keyword == "cleanstop" and value in ('yes', 'no'):
                    pass
                elif keyword == "smtp":
                    # valide server address
                    pass
                elif keyword == "maintenancedir":
                    pass
                else:
                    print "[PARSE ERROR] Line: " + str(counter) + " - unkown directive"
                    print line
                    return False
        return True

    def parse_virtual(self, text, counter, af_inet6):
        """Parse contents of the virutal section"""
        # Various regexp to match directives under virtual
        (k, sep, v) = text.partition("=")
        keyword = k.rstrip()
        value = v.lstrip().rstrip()

        if value == '':
            print "[PARSE ERROR] no value provided in line: " + str(counter)

        if keyword == "real" :
            if af_inet6 is not None:
                print "[PARSE ERROR] Line: " + str(counter) + " - Please use the correct address family in real server section."
                print text
                return False
        elif keyword == "real6":
            if af_inet6 is None:
                print "[PARSE ERROR] Line: " + str(counter) + " - Please use the correct address family in real server section."
                print text
                return False
        elif keyword == "request" and utils.has_quotes(value):
            pass
        elif keyword == "receive" and utils.has_quotes(value):
            pass
        elif keyword == "checktype":
            checktypes = ("connect", "negotiate", "ping", "off", "on", "external", "external-perl")
            if value.isdigit() or value in checktypes:
                pass
            else:
                print "[PARSE ERROR] Line: " + str(counter) + " - checktype must be one of " + str(checktypes)
                return False
        elif keyword == "checkcommand" and utils.has_quotes(value):
            pass
        elif keyword == "checktimeout" and value.isdigit():
            pass
        elif keyword == "negotiatetimeout" and value.isdigit():
            pass
        elif keyword == "checkcount" and value.isdigit():
            pass
        elif keyword == "failurecount" and value.isdigit():
            pass
        elif keyword == "checkinterval" and value.isdigit():
            pass
        elif keyword == "checkport" and value.isdigit():
            if int(value) < 1 or int(value) > 65536:
                print "[PARSE ERROR] Line: " + str(counter) + " - checkport must be in range 1-65536"
                return False
        elif keyword == "login" and utils.has_quotes(value):
            pass
        elif keyword == "passwd" and utils.has_quotes(value):
            pass
        elif keyword == "database" and utils.has_quotes(value):
            pass
        elif keyword == "secret" and utils.has_quotes(value):
            pass
        elif keyword == "load" and utils.has_quotes(value):
            pass
        elif keyword == "scheduler" and value.isalpha() and value.islower():
            schedulers = ('rr', 'wrr', 'lc', 'wlc', 'lblc', 'lblcr', 'dh', 'sh', 'sed', 'nq')
            if value in schedulers:
                pass
            else:
                print "[PARSE ERROR] Line: " + str(counter) + " - scheduler must be one of " + str(schedulers)
                return False
        elif keyword == "persistent" and value.isdigit():
            pass
        elif keyword == "netmask":
            if af_inet6:
                if value.isdigit() and int(value) >= 1 and int(value) <= 128:
                    pass
                else:
                    print "[PARSE ERROR] Line: " + str(counter) + " - value must be between 1 and 128"
                    return False
            else:
                if utils.check_ipv4(value):
                    pass
                else:
                    print "[PARSE ERROR] Line: " + str(counter) + " - dotted quad notation is required for netmask"
                    return False
        elif keyword == "protocol":
            if value == "fwm":
                # we also have to compare it to the virtual FWM value
                pass
            elif value == "tcp" or value == "udp":
                pass
            else:
                print "[PARSE ERROR] Line: " + str(counter) + " - protocol must be one of udp, tcp, or fwm"
                return False
        elif keyword == "service":
            services = ("dns" ,
                   "ftp"   ,
                   "http"  ,
                   "https" ,
                   "http_proxy" ,
                   "imap"  ,
                   "imaps" ,
                   "ldap"  ,
                   "nntp"  ,
                   "mysql" ,
                   "none"  ,
                   "oracle",
                   "pop"   ,
                   "pops"  ,
                   "radius",
                   "pgsql" ,
                   "sip"   ,
                   "smtp"  ,
                   "submission" ,
                   "simpletcp")
            if value in services:
                pass
            else:
                print "[PARSE ERROR] Line: " + str(counter) + " - service must be one of " + str(services)
                return False
        elif keyword == "httpmethod":
            if value.upper() == "GET" or value.upper() == "HEAD":
                pass
            else:
                print "[PARSE ERROR] Line: " + str(counter) + " - httpmethod must be one of ('GET', 'HEAD')"
                return False
        elif keyword == "virtualhost":
            pass
        elif keyword == "fallback":
            if af_inet6:
                print "[PARSE ERROR] Line: " + str(counter) + " - cannot define IPv4 fallback"
                return False
            else:
                # validate IPv6 address format
                pass
        elif keyword == "fallback6":
            if af_inet6:
                # validate IPv4 address format
                pass
            else:
                print "[PARSE ERROR] Line: " + str(counter) + " - cannot define IPv6 fallback"
                return False
        elif keyword == "fallbackcommand":
            pass
        elif keyword == "quiescent" and value in ('yes', 'no'):
            pass
        elif keyword == "emailalert":
            # validate email address formatting
            pass
        elif keyword == "emailalertfreq" and value.isdigit():
            pass
        elif keyword == "emailalertstatus":
            # validate status
            pass
        elif keyword == "monitorfile":
            try:
                open(value)
            except IOError as e:
                print "[ERROR] problem reading monitor file"
                return False
        elif keyword == "cleanstop" and value in ('yes', 'no'):
            pass
        elif keyword == "smtp":
            pass
        else:
            print text.rstrip()
            return False
        return True