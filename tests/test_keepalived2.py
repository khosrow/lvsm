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
        self.director = keepalived.Keepalived(path + '/scripts/ipvsadm3',
                                              path + '/etc/keepalived.conf',
                                              restart_cmd='',
                                              nodes='',
                                              args=args)

    def test_show(self):
        self.maxDiff = None
        # Testing show on non-standard ports
        expected_result =   ['',
                            'Layer 4 Load balancing',
                            '======================',
                            'TCP  192.0.2.2:8888                           rr     ',
                            '  -> 192.0.2.200:8888                         Masq    1      0          0         ',
                            '  -> 192.0.2.201:8888                         Masq    1      0          0         ',
                            '',
                            'UDP  192.0.2.2:domain                         rr     ',
                            '  -> 192.0.2.202:domain                       Masq    1      0          0         ',
                            '  -> 192.0.2.203:domain                       Masq    1      0          0         ',
                            '',
                            '']
        self.assertEqual(self.director.show(numeric=False, color=False), expected_result)

if __name__ == "__main__":
    unittest.main()
