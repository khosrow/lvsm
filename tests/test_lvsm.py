import unittest
import os
import sys
import StringIO

from lvsm import lvsm

path = os.path.abspath(os.path.dirname(__file__))


class TestConfig(unittest.TestCase):
    """Verify correct functionality in configure"""
    config = {'director_config': path + '/etc/ldirectord.conf',
              'firewall_config': path + '/etc/iptables.rules',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': ''
              }
    shell = lvsm.ConfigurePrompt(config)

    def test_showdirector(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = "# director config\n"
        self.shell.onecmd(' show director')
        result = output.getvalue()
        self.assertEqual(result, expected_result)

    def test_showfirewall(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = "# iptables\n"
        self.shell.onecmd(' show firewall')
        result = output.getvalue()
        self.assertEqual(result, expected_result)

    # def test_sync(self):
    #   output = StringIO.StringIO()
    #   sys.stdout = output
    #   expected_result = ""
    #   self.shell.onecmd(' sync')
    #   result = output.getvalue()
    #   self.assertEqual(result, expected_result)

    # def test_editdirector(self):
    #   output = StringIO.StringIO()
    #   sys.stdout = output
    #   expected_result = ""
    #   self.shell.onecmd(' edit director')
    #   result = output.getvalue()
    #   self.assertEqual(result, expected_result)


class TestConfigErrors(unittest.TestCase):
    """Verify error checking in configure"""
    def test_showdirector(self):
        self.assertTrue(True)

    def test_showfirewall(self):
        self.assertTrue(True)


class TestStatus(unittest.TestCase):
    config = {'ipvsadm': path + '/scripts/ipvsadm',
              'iptables': path + '/scripts/iptables',
              'director_config': path + '/etc/ldirectord.conf',
              'firewall_config': path + '/etc/iptables.rules',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': path + '/maintenance'
              }
    shell = lvsm.StatusPrompt(config)

    def test_showdirector(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  www.example.com:http         rr
  -> google.com:http              Masq    1      0          0
  -> slashdot.org:http            Masq    1      0          0
UDP  example.org:domain           rr
  -> resolver1.opendns.com:domain Masq    1      0          0
  -> resolver1.opendns.com:domain Masq    1      0          0"""
        self.shell.onecmd(' show director')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showfirewall(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """Chain INPUT (policy ACCEPT)
target     prot opt source               destination

Chain FORWARD (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination"""
        self.shell.onecmd(' show firewall')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showvirtualtcp(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  www.example.com:http         rr
  -> google.com:http              Masq    1      0          0
  -> slashdot.org:http            Masq    1      0          0"""
        self.shell.onecmd(' show virtual tcp www.example.com http')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showvirtualudp(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
UDP  example.org:domain           rr
  -> resolver1.opendns.com:domain Masq    1      0          0
  -> resolver1.opendns.com:domain Masq    1      0          0"""
        self.shell.onecmd(' show virtual udp example.org 53')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showrealactive(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """
Active servers:
---------------
TCP 43-10.any.icann.org:http
  -> slashdot.org:http"""
        self.shell.onecmd(' show real slashdot.org 80')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showrealdisabled(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """
Disabled servers:
-----------------
43-7.any.icann.org:http"""
        self.shell.onecmd(' show real 192.0.43.7 80')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_disablereal(self):
        self.assertTrue(True)

    def test_enablereal(self):
        self.assertTrue(True)


class TestStatusErrors(unittest.TestCase):
    def test_showdirector(self):
        self.assertTrue(True)

    def test_showfirewall(self):
        self.assertTrue(True)
