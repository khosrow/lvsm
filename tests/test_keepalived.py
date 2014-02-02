import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lvsm')))


from lvsm.modules import keepalived


class Keepalived(unittest.TestCase):
    """Tests for the functionality of the keepalived module"""
    def setUp(self):
        args = {'keepalived-mib': 'KEEPALIVED-MIB',
                'snmp_community': 'private',
                'snmp_host': 'localhost',
                'snmp_user': '',
                'snmp_password': '',
                'cache_dir': path + '/cache'
                }
        self.director = keepalived.Keepalived(path + '/scripts/ipvsadm2',
                                              path + '/etc/keepalived.conf',
                                              restart_cmd='',
                                              nodes='',
                                              args=args)

    def test_disablehost(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.cache_dir + '/realServerWeight.2.1'
        self.assertTrue(self.director.disable('resolver1.opendns.com'))
        
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError:
            pass
    
    def test_disablehostport(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.cache_dir + '/realServerWeight.2.1'
        self.assertTrue(self.director.disable('resolver1.opendns.com', 'domain'))
        
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError:
            pass

    def test_enablehost(self):
        output = StringIO.StringIO()
        sys.stdout = output

        filepath = self.director.cache_dir + '/realServerWeight.2.2'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.write('1')
            f.close()
            self.assertTrue(self.director.enable('resolver2.opendns.com'))
        except IOError:
            pass

    def test_enablehostport(self):
        output = StringIO.StringIO()
        sys.stdout = output

        filepath = self.director.cache_dir + '/realServerWeight.2.2'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.write('1')
            f.close()
            self.assertTrue(self.director.enable('resolver2.opendns.com', 'domain'))
        except IOError:
            pass

    def test_parseconfig1(self):
        # Testing parser on a valid config file
        configfile = path + '/etc/keepalived.conf'
        self.assertTrue(self.director.parse_config(configfile))

    def test_parseconfig2(self):
        # Testing parser on an invalid config file
        configfile = path + '/etc/keepalived.conf-bad'
        self.assertFalse(self.director.parse_config(configfile))

if __name__ == "__main__":
    unittest.main()
