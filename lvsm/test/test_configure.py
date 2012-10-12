import unittest
import os
import sys
import StringIO

# TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
# sys.path.insert(0, os.path.realpath(os.path.join(TESTS_ROOT, '..')))

from lvsm.lvsm import ConfigurePrompt


class TestConfigModule(unittest.TestCase):
    config = {'director_config': './etc/ldirectord.conf',
              'firewall_config': './etc/iptables.rules',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': ''
              }
    # shell = lvsm.ConfigurePrompt(config)
    shell = ConfigurePrompt(config)

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
