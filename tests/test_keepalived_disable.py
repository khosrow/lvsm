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

    def tearDown(self):
        filepath1 = self.director.cache_dir + '/realServerWeight.2.1'
        filepath2 = self.director.cache_dir + '/realServerReason.2.1' 
        os.unlink(filepath1)
        os.unlink(filepath2)

    def test_disablehost(self):
        output = StringIO.StringIO()
        sys.stdout = output
        self.assertTrue(self.director.disable('udp', '192.0.2.202'))
        
    def test_disablehostport(self):
        output = StringIO.StringIO()
        sys.stdout = output
        self.assertTrue(self.director.disable('udp', '192.0.2.202', 'domain'))
        
if __name__ == "__main__":
    unittest.main()
