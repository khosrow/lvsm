
import os
import socket
import subprocess
import sys
import time
import logging
from pyparsing import *
from lvsm import utils, genericdirector
from lvsm.modules import ldparser

logger = logging.getLogger('lvsm')


class Ldirectord(genericdirector.GenericDirector):
    """Handles ldirector-specific functionality like enable/disable actions.
    """
    def __init__(self, ipvsadm, configfile='', restart_cmd='', nodes='', args=dict()):
        super(Ldirectord, self).__init__(ipvsadm, configfile, restart_cmd, nodes, args)
        try:
            f = open(self.configfile)
        except OSError as e:
            logger.error(e)

        self.maintenance_dir = ""

        for line in f:
            if line.find("maintenancedir") > -1:
                s, sep, path = line.partition('=')
                self.maintenance_dir = os.path.abspath(os.path.expanduser(os.path.expandvars(path.strip())))

    def disable(self, host, port='', reason=''):
        # Prepare a canned error message
        error_msg = "Problem disabling on remote node"
        if self.maintenance_dir:
            hostips = utils.gethostbyname_ex(host)
            if not hostips:
                return False

            # In disable cmd, we ignore if the host has more than one IP
            hostip = hostips[0]

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
                    logger.warning("host is already disabled!")
                    return True
            try:
                f = open(self.maintenance_dir + "/" + hostport, 'w')
                f.write(reason)
            except IOError as e:
                logger.error(e)
                return False

            # Copy the state file to other nodes
            fullpath = self.maintenance_dir + "/" + hostport
            self.filesync_nodes('copy', fullpath)

            # Confirm that it's removed from ldirector
            i = 0
            print "Disabling server ",
            while i < 10:
                sys.stdout.write(".")
                sys.stdout.flush()
                time.sleep(1)
                i = i + 1
                found = False

                output = self.show_running(numeric=True, color=False)
                for line in output:
                    if hostport in line:
                        found = True
                        break
                if not found:
                    print " OK"
                    break
            if found: 
                print " Failed"
            # note: even if the real is still showing up, we've created
            # the file, so we should still return true
            return True
        else:
            logger.error("maintenance_dir not defined in config.")
            return False

    def enable(self, host, port=''):
        """enable a previously disabled server"""
        # Prepare a canned error message.
        error_msg = "Problem enabling on remote node"
        
        hostips = utils.gethostbyname_ex(host)
        if not hostips:
            return False

        # In enable cmd, we ignore if the host has more than one IP
        hostip = hostips[0]

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
                        logger.error(e)
                        return False

                    # Remove the same file from other nodes in the cluster.
                    fullpath = self.maintenance_dir + "/" + filename
                    self.filesync_nodes('remove', fullpath)

                    # Wait 4.5 seconds before checking output of ipvsadm.
                    # This is an arbitrary number and could possibly be changed
                    i = 0
                    print "Enabling server ",
                    while i < 10:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        time.sleep(1)
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
            logger.error("Server not found in maintenance_dir!")
            return False
        else:
            logger.error("maintenance_dir not defined!")
            return False

    def show_real_disabled(self, host, port, numeric):
        """show status of disabled real server across multiple VIPs"""
        # note that host='' and port='' returns all disabled server
        if host and port:
            hostips = utils.gethostbyname_ex(host)
            if not hostips:
                return

            # Here we only use the first IP if a host has more than one
            hostip = hostips[0]
            
            portnum = utils.getportnum(port)
            if portnum == -1:
                return
            hostport = hostip + ":" + str(portnum)

        output = list()

        if not self.maintenance_dir:
            logger.error("maintenance_dir not defined!")
            return output

        # make sure to catch errors like related to maint_dir
        try:
            filenames = os.listdir(self.maintenance_dir)
        except (IOError, OSError) as e:
            logger.error("Config item maintenance_dir")
            logger.error(e)
            return output

        for filename in filenames:
            try:
                f = open(self.maintenance_dir + "/" + filename)
                reason = 'Reason: ' + f.readline()
                f.close()
            except IOError as e:
                reason = ''
                logger.error(e)
            if ((not host and not port) or
                self.convert_filename(filename) == hostip or
                self.convert_filename(filename) == hostip + ":" + str(portnum)):
            
                # decide if we have to convert to hostname or not
                if numeric:
                    output.append(filename + "\t\t" + reason)
                else:
                    rip = filename.split(":")[0]
                    try:
                        (ripname, al, ipl) = socket.gethostbyaddr(rip)
                    except socket.herror, e:
                        logger.error(e)
                        return False
                    if len(filename.split(":")) == 2:
                        ripport = filename.split(":")[1]
                        try:
                            ripportname = socket.getservbyport(int(ripport))
                        except socket.error as e:
                            ripportname = ripport
                        ripname = ripname + ':' + ripportname
                    else:
                        pass
                    output.append(ripname + "\t\t" + reason)
        return output

    def parse_config(self, configfile):
        """Read the config file and validate configuration syntax"""
        try:
            f = open(configfile)
        except IOError as e:
            logger.error(e)
            return False

        conf = "".join(f.readlines())
        tokens = ldparser.tokenize_config(conf)

        if tokens:
            return True
        else:
            return False
