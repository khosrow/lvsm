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
        expected_result = """Chain INPUT (policy ACCEPT)
target     prot opt source               destination
ACCEPT     tcp  --  anywhere             dinsdale.python.org tcp dpt:http

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination"""  
        lines = self.firewall.show(numeric=False, color=False)
        result = ''
        for line in lines:
            result = result + line + '\n'
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showvirtual(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = "ACCEPT     tcp  --  anywhere\
             dinsdale.python.org tcp dpt:http"
        lines = self.firewall.show_virtual('dinsdale.python.org', 'http', 'tcp',
                                           numeric=False, color=False)
        result = ''
        for line in lines:
            result = result + line + '\n'
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_shownat(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination

Chain INPUT (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination"""
        
        lines = self.firewall.show_nat(numeric=False)

        result = ''
        for line in lines:
            result = result + line + '\n'

        self.assertEqual(result.rstrip(), expected_result.rstrip())