import unittest
import os
import sys
import StringIO
from lvsm import firewall

path = os.path.abspath(os.path.dirname(__file__))


class FirewallTestCase(unittest.TestCase):
    """Testing firewall module"""
    def setUp(self):
        self.firewall = firewall.Firewall(path + '/scripts/iptables')

    def test_show(self):
        output = StringIO.StringIO()
        sys.stdout = output
        self.assertTrue(self.firewall.show(numeric=False))

    def test_showvirtual(self):
        output = StringIO.StringIO()
        sys.stdout = output
        self.assertTrue(self.firewall.show_virtual('www.example.com', 'http',
                        numeric=False))
