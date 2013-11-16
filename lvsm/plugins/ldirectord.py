
import os
import socket
import subprocess
import sys
import time
import logging
from pyparsing import *

# from lvsm import utils
# from lvsm import genericdirector
import lvsm

logger = logging.getLogger('lvsm')


class Ldirectord(lvsm.genericdirector.GenericDirector):
    """Handles ldirector-specific functionality like enable/disable actions.
    """
    def __init__(self, maintenance_dir, ipvsadm,
                 configfile='', restart_cmd='', nodes=''):
        super(Ldirectord, self).__init__(maintenance_dir, ipvsadm,
                                         configfile, restart_cmd, nodes)

    def disable(self, host, port='', reason=''):
        # Prepare a canned error message
        error_msg = "Problem disabling on remote node"
        if self.maintenance_dir:
            hostip = lvsm.utils.gethostname(host)
            if not hostip:
                return False
            if port:
                # check that it's a valid port
                portnum = lvsm.utils.getportnum(port)
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
                logger.error(e)
                return False

            if self.nodes is not None:
                filename = self.maintenance_dir + "/" + hostport
                for node in self.nodes:
                    if node != self.hostname:
                        remote = node + ":" + self.maintenance_dir
                        args = ['scp', filename, remote]
                        logger.debug('Running command : %s' % (' '.join(args)))
                        try:
                            output = lvsm.utils.check_output(args)
                        except OSError as e:
                            # print error_msg + e.strerror
                            logger.error(error_msg)
                            logger.error(e)
                        except subprocess.CalledProcessError as e:
                            # print error_msg + e.output
                            logger.error(error_msg)
                            logger.error(e)
            # now confirm that it's removed from ldirector
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
            # print "[ERROR] maintenance_dir not defined in config."
            logger.error("maintenance_dir not defined in config.")
            return False

    def enable(self, host, port=''):
        """enable a previously disabled server"""
        # Prepare a canned error message.
        error_msg = "Problem enabling on remote node"
        hostip = lvsm.utils.gethostname(host)
        if not hostip:
            return False
        # If port was provided the file will be of form xx.xx.xx.xx:nn
        if port:
            # Check that the port is valid.
            portnum = lvsm.utils.getportnum(port)
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
                    if self.nodes is not None:
                        for node in self.nodes:
                            if node != self.hostname:
                                cmd = "rm " + self.maintenance_dir + "/" + filename
                                args = ['ssh', node, cmd]
                                logger.debug('Running command : %s' % (' '.join(args)))
                                try:
                                    output = lvsm.utils.check_output(args)
                                except OSError as e:
                                    # print error_msg + e.strerror
                                    logger.error(error_msg)
                                    logger.error(e)
                                except subprocess.CalledProcessError as e:
                                    # print error_msg + e.output
                                    logger.error(error_msg)
                                    logger.error(e)
                    # Wait 4.5 seconds before checking output of ipvsadm.
                    i = 0
                    found = False
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
            # print "[ERROR] Server not found in maintenance_dir!"
            logger.error("Server not found in maintenance_dir!")
            return False
        else:
            # print "[ERROR] maintenance_dir not defined!"
            logger.error("maintenance_dir not defined!")
            return False

    def show_real_disabled(self, host, port, numeric):
        """show status of disabled real server across multiple VIPs"""
        # note that host='' and port='' returns all disabled server
        if host and port:
            hostip = lvsm.utils.gethostname(host)
            if not hostip:
                return
            portnum = lvsm.utils.getportnum(port)
            if portnum == -1:
                return
            hostport = hostip + ":" + str(portnum)
        # output = ["", "Disabled servers:", "-----------------"]
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
            except IOError as e:
                reason = ''
                logger.error(e)
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
            print "[ERROR] " + e.strerror
            return False

        conf = "".join(f.readlines())
        tokens = self.tokenize_config(conf)

        if tokens:
            return True
        else:
            return False

    def tokenize_config(self, configfile):
        """Tokenize the config file. This method will do the bulk of the 
        parsing. Additional verifications can be made in parse_config"""
        # Needed to parse the tabbed ldirector config
        indentStack = [1]

        # Define statics
        EQUAL = Literal("=").suppress()
        COLON = Literal(":").suppress()
        # INDENT = White("    ").suppress()
        # INDENT = Regex("^ {4,}").suppress()

        ## Define parsing rules for single lines
        hostname = Word(alphanums + '._+-')
        ip4_address = Combine(Word(nums) - ('.' + Word(nums)) * 3)
        ip4_address.setParseAction(self.validate_ip4)

        port = Word(alphanums)
        port.setParseAction(self.validate_port)

        lbmethod = Word(alphas)
        lbmethod.setParseAction(self.validate_lbmethod)

        ip4_addrport = (ip4_address | hostname) + COLON + port
        # Validate port numbers
        # ip4_addrport.setParseAction(validate_port)

        yesno = Word(printables)
        yesno.setParseAction(self.validate_yesno)

        integer = Word(printables)
        integer.setParseAction(self.validate_int)

        send_receive = dblQuotedString + Literal(",") + dblQuotedString

        real4 = Group(Literal("real") + EQUAL + ip4_addrport + lbmethod + Optional(Word(nums)) + Optional(send_receive))
        # real4 = Group(Literal("real") + EQUAL + ip4_addrport + lbmethod + Optional(Word(nums)) + Optional(Word(dblQuotedString) + Word(dblQuotedString)))
        virtual4 = Group(Literal("virtual") + EQUAL + ip4_addrport)
        comment = Literal("#") + Optional(restOfLine)

        # Optional keywords
        optionals = Forward()
        autoreload = Group(Literal("autoreload") + EQUAL + yesno)
        callback = Group(Literal("callback") + EQUAL + dblQuotedString)
        checkcommand = Group(Literal("checkcommand") + EQUAL + (dblQuotedString | Word(printables)))
        # checkinterval = Group(Literal("checkinterval") + EQUAL + Word(alphanums))
        checkinterval = Group(Literal("checkinterval") + EQUAL + integer)
        checktimeout = Group(Literal("checktimeout") + EQUAL + integer)
        checktype = Group(Literal("checktype") + EQUAL + Word(alphanums))
        checkport = Group(Literal("checkport") + EQUAL + Word(alphanums))
        cleanstop = Group(Literal("cleanstop") + EQUAL + yesno)
        database = Group(Literal("database") + EQUAL + dblQuotedString)
        emailalert = Group(Literal("emailalert") + EQUAL + Word(printables))
        emailalertfreq = Group(Literal("emailalertfreq") + EQUAL + integer)
        emailalertfrom = Group(Literal("emailalertfrom") + EQUAL + Word(printables))
        emailalertstatus = Group(Literal("emailalertstatus") + EQUAL + Word(printables))
        execute = Group(Literal("execute") + EQUAL + Word(printables))
        failurecount = Group(Literal("failurecount") + EQUAL + integer)
        # fallback = Group(Literal("fallback") + EQUAL + ip4_addrport + Optional(lbmethod, default=''))
        fallback = Group(Literal("fallback") + EQUAL + ip4_addrport )
        fallbackcommand = Group(Literal("fallbackcommand") + EQUAL + (dblQuotedString | Word(printables)))
        fork = Group(Literal("fork") + EQUAL + yesno)
        httpmethod = Group(Literal("httpmethod") + EQUAL + Word(alphanums))
        load = Group(Literal("load") + EQUAL + dblQuotedString)
        logfile = Group(Literal("logfile") + EQUAL + Word(printables))
        login = Group(Literal("login") + EQUAL + dblQuotedString)
        maintenancedir = Group(Literal("maintenancedir") + EQUAL + Word(printables))
        monitorfile = Group(Literal("monitorfile") + EQUAL + (dblQuotedString | Word(printables)))
        negotiatetimeout = Group(Literal("negotiatetimeout") + EQUAL + integer)
        netmask = Group(Literal("netmask") + EQUAL + ip4_address)
        passwd = Group(Literal("passwd") + EQUAL + dblQuotedString)
        persistent = Group(Literal("persistent") + EQUAL + integer)
        protocol = Group(Literal("protocol") + EQUAL + Word(alphas))
        quiescent = Group(Literal("quiescent") + EQUAL + yesno)
        readdquiescent = Group(Literal("readdquiescent") + EQUAL + yesno)
        receive = Group(Literal("receive") + EQUAL + dblQuotedString)
        request = Group(Literal("request") + EQUAL + dblQuotedString)
        scheduler = Group(Literal("scheduler") + EQUAL + Word(alphas))
        secret = Group(Literal("secret") + EQUAL + dblQuotedString)
        service = Group(Literal("service") + EQUAL + Word(alphas))
        supervised = Group(Literal("supervised") + EQUAL + yesno)
        smtp = Group(Literal("smtp") + EQUAL + (ip4_address | hostname))
        virtualhost = Group(Literal("virtualhost") + EQUAL + '"' + hostname + '"' )

        # Validate all the matched elements
        checkport.setParseAction(self.validate_port)
        checktype.setParseAction(self.validate_checktype)
        httpmethod.setParseAction(self.validate_httpmethod)
        protocol.setParseAction(self.validate_protocol)
        scheduler.setParseAction(self.validate_scheduler)
        service.setParseAction(self.validate_service)

        # TODO: validate protocol with respect to the virtual directive
        # TODO: implement virtual6, real6, fallback6

        optionals << ( checkcommand | checkinterval | checktimeout | checktype | checkport | cleanstop
                    | database | emailalert | emailalertfreq | emailalertstatus | failurecount | fallback
                    | fallbackcommand | httpmethod | load | login | monitorfile | negotiatetimeout | netmask
                    | passwd | persistent | protocol | quiescent | receive | request | scheduler | secret
                    | service | smtp | virtualhost)
        # optionals = ( checkcommand | checkinterval | checktimeout | checktype | checkport | cleanstop
        #             | database | emailalert | emailalertfreq | emailalertstatus | failurecount | fallback
        #             | fallbackcommand | httpmethod | load | login | monitorfile | negotiatetimeout | netmask
        #             | passwd | persistent | protocol | quiescent | receive | request | scheduler | secret
        #             | service | smtp | virtualhost)

        glb_optionals = ( checktimeout | negotiatetimeout | checkinterval | failurecount | fallback
                        | fallbackcommand | autoreload | callback | logfile | execute | fork | supervised
                        | quiescent | readdquiescent | emailalert | emailalertfreq | emailalertstatus
                        | emailalertfrom | cleanstop | smtp | maintenancedir )

        ## Define block of config
        # both of the next two styles works
        # virtual4_keywords = indentedBlock(OneOrMore(real4 & ZeroOrMore(optionals)), indentStack, True)
        # virtual4_block = virtual4 + virtual4_keywords
        virtual4_keywords = OneOrMore(real4) & ZeroOrMore(optionals)
        virtual4_block = virtual4 + indentedBlock(virtual4_keywords, indentStack, True)

        virtual4_block.ignore(comment)

        allconfig = OneOrMore(virtual4_block) & ZeroOrMore(glb_optionals)
        allconfig.ignore(comment)

        try:
            tokens = allconfig.parseString(configfile)
        except ParseException as pe:
            print "[ERROR] While parsing config file"
            print pe
        except ParseFatalException as pe:
            print "[ERROR] While parsing config file"
            print pe
        else:
            return tokens
        finally:
            pass
