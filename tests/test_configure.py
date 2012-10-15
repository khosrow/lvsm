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
    def test_printconfig(self):
        self.assertTrue(True)
