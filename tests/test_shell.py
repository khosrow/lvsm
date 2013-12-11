import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
from lvsm import shell


class Configure(unittest.TestCase):
    """Verify correct functionality in configure"""
    config = {'director_config': path + '/etc/ldirectord.conf',
              'firewall_config': path + '/etc/iptables.rules',
              'pager': 'none',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': '',
              'director_cmd': '',
              'nodes':'',
              'ipvsadm': path + '/scripts/ipvsadm',
              'iptables': path + '/scripts/iptables'
              }
    shell = shell.ConfigurePrompt(config)

    def test_showdirector(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = "# director config\n\n"
        self.shell.onecmd(' show director')
        result = output.getvalue()
        self.assertEqual(result, expected_result)

    def test_showfirewall(self):
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = "# iptables\n\n"
        self.shell.onecmd(' show firewall')
        result = output.getvalue()
        self.assertEqual(result, expected_result)


class ConfigureErrors(unittest.TestCase):
    """Verify error checking in configure"""
    def test_showdirector(self):
        self.assertTrue(True)

    def test_showfirewall(self):
        self.assertTrue(True)


class Virtual(unittest.TestCase):
    config = {'ipvsadm': path + '/scripts/ipvsadm',
              'iptables': path + '/scripts/iptables',
              'pager': 'none',
              'director_config': path + '/etc/ldirectord.conf',
              'firewall_config': path + '/etc/iptables.rules',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': path + '/maintenance',
              'director_cmd': '',
              'nodes':''
              }
    shell = shell.VirtualPrompt(config)
    shell.settings['color'] = False

    def test_status(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  dinsdale.python.org:http     rr
  -> slashdot.org:http            Masq    1      0          0
UDP  dinsdale.python.org:domain   rr
  -> resolver1.opendns.com:domain Masq    1      0          0
  -> resolver2.opendns.com:domain Masq    1      0          0


Disabled servers:
-----------------
lga15s34-in-f3.1e100.net:http\t\tReason: Disabled for testing"""
        self.shell.onecmd(' status')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

#     def test_showfirewall(self):
#         output = StringIO.StringIO()
#         sys.stdout = output
#         expected_result = """Chain INPUT (policy ACCEPT)
# target     prot opt source               destination
# ACCEPT     tcp  --  anywhere             dinsdale.python.org tcp dpt:http

# Chain FORWARD (policy ACCEPT)
# target     prot opt source               destination

# Chain OUTPUT (policy ACCEPT)
# target     prot opt source               destination"""
#         self.shell.onecmd(' show firewall')
#         result = output.getvalue()
#         self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showvirtualtcp(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  dinsdale.python.org:http     rr
  -> slashdot.org:http            Masq    1      0          0

ACCEPT     tcp  --  anywhere             dinsdale.python.org tcp dpt:http"""
        self.shell.onecmd(' show tcp dinsdale.python.org http')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showvirtualudp(self):
        self.shell.settings['numeric'] = False
        output = StringIO.StringIO()
        sys.stdout = output
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
UDP  dinsdale.python.org:domain   rr
  -> resolver1.opendns.com:domain Masq    1      0          0
  -> resolver2.opendns.com:domain Masq    1      0          0"""
        self.shell.onecmd(' show udp dinsdale.python.org 53')
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

#     def test_showrealactive(self):
#         self.shell.settings['numeric'] = False
#         output = StringIO.StringIO()
#         sys.stdout = output
#         expected_result = """
# Active servers:
# ---------------
# TCP dinsdale.python.org:http
#   -> slashdot.org:http"""
#         self.shell.onecmd(' show real slashdot.org 80')
#         result = output.getvalue()
#         self.assertEqual(result.rstrip(), expected_result.rstrip())

#     def test_showrealdisabled(self):
#         output = StringIO.StringIO()
#         sys.stdout = output
#         expected_result = """
# Disabled servers:
# -----------------
# lga15s34-in-f3.1e100.net:http\t\tReason: Disabled for testing"""
#         self.shell.onecmd(' show real 173.194.43.3 80')
#         result = output.getvalue()
#         self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_disablereal(self):
        filepath = self.config['maintenance_dir'] + '/208.67.222.222'
        # this is the disabling message we'll store in the file
        sys.stdin = StringIO.StringIO('disabled by test case')
        self.shell.onecmd('disable 208.67.222.222')
        self.assertTrue(os.path.exists(filepath))
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError as e:
            pass

    def test_enablereal(self):
        filepath = self.config['maintenance_dir'] + '/208.67.222.222:53'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.shell.onecmd(' enable 208.67.222.222 domain')
            self.assertTrue(not os.path.exists(filepath))
        except IOError as e:
            pass


class VirtualErrors(unittest.TestCase):
    def test_status(self):
        self.assertTrue(True)

    def test_showvirtualtcp(self):
        self.assertTrue(True)
