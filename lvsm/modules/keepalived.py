import logging
import os
import socket
from lvsm import genericdirector, utils
from lvsm.modules import kaparser

logger = logging.getLogger('lvsm')

# needed for testing the code on non-Linux platforms
try:
    from snimpy import manager
    from snimpy import mib
    from snimpy import snmp
except ImportError:
    logger.warn("Python module 'snimpy' not found, loading a dummy module.")
    logger.warn("'enable' and 'disable' commands will not be availble.""")
    from lvsm.snimpy_dummy import manager
    from lvsm.snimpy_dummy import mib
    from lvsm.snimpy_dummy import snmp
    
class Keepalived(genericdirector.GenericDirector):
    """
    Implements Keepalived specific functions. Stub for now.
    """
    def __init__(self, ipvsadm, configfile='', restart_cmd='', nodes='', args=dict()):
        super(Keepalived, self).__init__(ipvsadm,
                                         configfile,
                                         restart_cmd,
                                         nodes,
                                         args)
        # Now handle args
        self.mib = args['keepalived-mib']
        self.snmp_community = args['snmp_community']
        self.snmp_host = args['snmp_host']
        if args['snmp_user']:
            self.snmp_user = args['snmp_user']
        else:
            self.snmp_user = None

        if args['snmp_password']:
            self.snmp_password = args['snmp_password']
        else:
            self.snmp_password = None
 
        self.cache_dir = args['cache_dir']

    def disable(self, host, port='', vhost='', vport='', reason=''):
        """
        Disable a real server in keepalived. This command rellies on snimpy
        and will set the weight of the real server to 0.
        The reason is not used in this case.
        """
        found = False

        hostip = utils.gethostname(host)
        if not hostip:
            logger.error('Real server %s is not valid!' % host)
            return False
        if port:
            # check that it's a valid port
            portnum = utils.getportnum(port)
            if portnum == -1:
                logger.error('Port %s is not valid!' % port)
                return False
        
        if vhost:
            vipnum = utils.gethostname(vhost)
            if not vipnum:
                logger.error('Virtual host %s not valid!' % vhost)
                return False
        if vport:
            vportnum = utils.getportnum(vport)
            if vportnum == -1:
                logger.error('Virtual port %s is not valid!' % vport)
                return False
        
        try:
            manager.load(self.mib)
            m = manager.Manager(self.snmp_host,  
                                self.snmp_community,
                                secname=self.snmp_user,
                                authpassword=self.snmp_password)
        except (snmp.SNMPException, mib.SMIException) as e:
            logger.error(e)
            logger.error("Unable to perfrom action!")
            return False

        # iterate through the virtual servers
        # and disable the matching real server
        try:
            for i in m.virtualServerAddress:
                hexip = m.virtualServerAddress[i]
                vip = socket.inet_ntoa(hexip)
                logger.debug("Checking VIP: %s" % vip)
                if not vhost or vipnum == vip:
                    vp = m.virtualServerPort[i]
                    if not vport or vportnum == vp:
                        # iterate over the realservers in 
                        # the specific virtual
                        j = m.virtualServerRealServersTotal[i]
                        idx = 1                    
                        while idx <= j:
                            hexip = m.realServerAddress[i,idx]
                            rip = socket.inet_ntoa(hexip)
                            rp = m.realServerPort[i,idx]
                            if hostip == rip:                                                        
                                if not port or (port and portnum == rp):
                                        logger.debug('Disabling %s:%s on VIP %s:%s' % (rip, rp, vip, vp))
                                        # 'found' is used to keep track if we find a matching real to disable
                                        found = True

                                        # Record the original weight somewhere before disabling it
                                        # Will be used when enabling the server
                                        weight = m.realServerWeight[i,idx]
                                        logger.debug('Current weight: %s' % weight)

                                        if weight == 0:
                                            logger.warning("Real server %s:%s is already disabled on VIP %s:%s" % (rip, rp, vip, vp))
                                            idx += 1
                                            continue

                                        filename = "realServerWeight.%s.%s" % (i, idx)
                                        fullpath = '%s/%s' % (self.cache_dir, filename)
                                        try:
                                            logger.info('Creating file: %s' % fullpath)
                                            f = open(fullpath, 'w')
                                            f.write(str(weight))
                                            f.close()
                                        except IOError as e:
                                            logger.error(e)
                                            logger.error('Please make sure %s is writable before proceeding!' % self.cache_dir)
                                            return False 

                                        # Copy the file to the other nodes
                                        # In case of a switch lvsm will have 
                                        # the weight info on all nodes
                                        self.filesync_nodes('copy', fullpath)
                            
                                        # set the weight to zero
                                        community = "private"
                                        cmd_example = "snmpset -v2c -c %s localhost KEEPALIVED-MIB::%s = 0" % (community, filename)
                                        logger.info("Running equivalent command to: %s" % cmd_example)
                                        m.realServerWeight[i,idx] = 0
                                        print "Disabled %s:%s on VIP %s:%s. Weight set to 0." % (rip, rp, vip, vp)
                            idx += 1
        except snmp.SNMPException as e:
            logger.error(e)
            logger.error("Unable to complete the command successfully! Please verify manually.")
            return False 

        if not found:
            logger.error('No matching real servers were found!')
            return False
        else:
            return True

    def enable(self, rhost, rport='',vhost='', vport=''):
        """
        Enable a real server in keepalived. This command rellies on snimpy
        and will set the weight of the real server back to its original weight. 
        Assumption: original weight is stored in self.cache_dir/realServerWeight.x.y
        The reason is not used in this case.
        """
        hostip = utils.gethostname(rhost)
        if not hostip:
            logger.error('Real server %s is not valid!' % rhost)
            return False
        if rport:
            # check that it's a valid port
            portnum = utils.getportnum(rport)
            if portnum == -1:
                logger.error('Port %s is not valid!' % rport)
                return False
        
        if vhost:
            vipnum = utils.gethostname(vhost)
            if not vipnum:
                logger.error('Virtual host %s not valid!' % vhost)
                return False
        if vport:
            vportnum = utils.getportnum(vport)
            if vportnum == -1:
                logger.error('Virtual port %s is not valid!' % vport)
                return False
        
        try:
            manager.load(self.mib)
            m = manager.Manager(self.snmp_host,
                                self.snmp_community,
                                secname=self.snmp_user,
                                authpassword=self.snmp_password)
        except (snmp.SNMPException, mib.SMIException) as e:
            logger.error(e)
            logger.error("Unable to perfrom action!")
            return False

        # iterate through the virtual servers
        # and enable the matching real server
        # if the weight is zero.
        # Note: if file is not found in the cache_dir (i.e. /var/cache/lvsm)
        # we set the weight 1 (keepalived default)
        try:
            for i in m.virtualServerAddress:
                hexip = m.virtualServerAddress[i]
                vip = socket.inet_ntoa(hexip)
                logger.debug("Checking VIP: %s" % vip)
                if not vhost or vipnum == vip:
                    vp = m.virtualServerPort[i]
                    if not vport or vportnum == vp:
                        # iterate over the realservers in 
                        # the specific virtual host
                        j = m.virtualServerRealServersTotal[i]
                        idx = 1
                        while idx <= j:
                            hexip = m.realServerAddress[i,idx]
                            rip = socket.inet_ntoa(hexip)
                            rp = m.realServerPort[i,idx]
                            if hostip == rip:
                                if not rport or (rport and portnum == rp):
                                        # Record the original weight somewhere before disabling it
                                        # Will be used when enabling the server
                                        weight = m.realServerWeight[i,idx]
                                        logger.debug('Current weight: %s' % weight)
                                        if weight > 0:
                                            msg = "Real server %s:%s on VIP %s:%s is already enabled with a weight of %s" % (rip, rp, vip, vp, weight)
                                            logger.warning(msg)
                                            idx += 1 
                                            continue

                                        filename = "realServerWeight.%s.%s" % (i, idx)
                                        fullpath = '%s/%s' % (self.cache_dir, filename)

                                        logger.debug('Enabling %s:%s on VIP %s:%s' % (rip, rp, vip, vp))
                                        try:
                                            logger.debug('Reading server weight from file: %s' % fullpath)
                                            f = open(fullpath, 'r')
                                            str_weight = f.readline().rstrip()
                                            f.close()
                                            # make sure the weight is a valid int 
                                            orig_weight = int(str_weight) 
                                        except IOError as e:
                                            logger.warning("%s. Using 1 as default weight!" % e)
                                            logger.warning("To ensure the correct wieght is set, please restart Keepalived.")
                                            orig_weight = 1
                                       
                                        # set the weight to zero
                                        community = "private"
                                        cmd_example = "snmpset -v2c -c %s localhost KEEPALIVED-MIB::%s = %s" % (community, filename, orig_weight)
                                        logger.info("Running equivalent command to: %s" % cmd_example)
                                        m.realServerWeight[i,idx] = orig_weight
                                        print "Enabled %s:%s on VIP %s:%s. Weight set to %s." % (rip, rp, vip, vp, orig_weight)

                                        # Now remove the placeholder file locally
                                        try:
                                            os.unlink(fullpath)
                                        except OSError as e:
                                            logger.error(e)
                                            logger.error('Please make sure %s is writable!' % self.cache_dir)
                                            logger.error('%s needs to be manually deleted to avoid future problems.' % fullpath)

                                        # remove the placeholder file in other nodes
                                        self.filesync_nodes('remove', fullpath)


                            idx += 1
        except snmp.SNMPException as e:
            logger.error(e)
            logger.error("Unable to complete the command successfully! Please verify manually.")
            return False 

        return True

    def show_real_disabled(self, host, port, numeric):
        """show status of disabled real server across multiple VIPs"""

        output = list()

        # update the ipvs table
        self.build_ipvs()
        for v in self.virtuals:
            for r in v.realServers:
                if r.weight == "0":
                    if numeric:
                        output.append("%s:%s" % (r.ip, r.port))
                    else:
                        host, aliaslist, ipaddrlist = socket.gethostbyaddr(r.ip)
                        portname = socket.getservbyport(int(r.port))
                        output.append("%s:%s" % (host, portname))

        return output

    def parse_config(self, configfile):
        """Read the config file and validate configuration syntax"""
        try:
            f = open(configfile)
        except IOError as e:
            logger.error(e)
            return False

        conf = "".join(f.readlines())
        tokens = kaparser.tokenize_config(conf)

        if tokens:
            return True
        else:
            return False
