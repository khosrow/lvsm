import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lvsm')))

from lvsm import firewall


class FirewallTestCase(unittest.TestCase):
    """Testing firewall module"""
    def setUp(self):
        self.firewall = firewall.Firewall(path + '/scripts/iptables')

    def test_show(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """
IP Packet filter rules
======================
Chain INPUT (policy ACCEPT)
target     prot opt source               destination
ACCEPT     tcp  --  anywhere             192.0.2.2 tcp dpt:80

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
        expected_result = """
IP Packet filter rules
======================
ACCEPT     tcp  --  anywhere\
             192.0.2.2 tcp dpt:80"""
        lines = self.firewall.show_virtual('192.0.2.2', 'http', 'tcp',
                                           numeric=False, color=False)
        result = ''
        for line in lines:
            result = result + line + '\n'
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_shownat(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """
NAT rules
=========
Chain PREROUTING (policy ACCEPT)
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


if __name__ == "__main__":
    unittest.main()
