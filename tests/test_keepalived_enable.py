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

        # create the file before we continue
        filepath1 = self.director.cache_dir + '/realServerWeight.2.2'
        filepath2 = self.director.cache_dir + '/realServerReason.2.2'
        f = open(filepath1, 'w')
        f.write('1')
        f.close()

        f = open(filepath2, 'w')
        f.write('test')
        f.close() 

    def test_enablehost(self):
        output = StringIO.StringIO()
        sys.stdout = output

        self.assertTrue(self.director.enable('udp', '192.0.2.203'))

    def test_enablehostport(self):
        output = StringIO.StringIO()
        sys.stdout = output

        self.assertTrue(self.director.enable('udp', '192.0.2.203', 'domain'))

if __name__ == "__main__":
    unittest.main()
