import unittest
import os
import sys
import StringIO

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTS_ROOT, '..')))

import lvsm


class TestStatusModule(unittest.TestCase):
    config = {'ipvsadm': './scripts/ipvsadm',
              'iptables': './scripts/iptables',
              'director_config': './etc/ldirectord.conf',
              'firewall_config': './etc/iptables.rules',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': ''
              }
    shell = lvsm.StatusPrompt(config)
  
    def test_showdirector(self):
      output = StringIO.StringIO()
      sys.stdout = output
      expected_result = "This is ipvsadm\n"
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
