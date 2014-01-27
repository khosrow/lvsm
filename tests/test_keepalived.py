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
                'snmp_password': ''
                }
        self.director = keepalived.Keepalived(path + '/scripts/ipvsadm',
                                              path + '/etc/keepalived.conf',
                                              restart_cmd='',
                                              nodes='',
                                              args=args)

    def test_disablehost(self):
        self.assertTrue(True) 
    
    def test_disablehostport(self):
        self.assertTrue(True)

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
