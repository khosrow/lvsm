import unittest
import os
import sys

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(TESTS_ROOT, '..')))

import lvsm
import director


class ConfigModuleTest(unittest.TestCase):
    buffer = True
    config = {'director_config': './etc/ldirectord.cf',
              'firewall_config': './etc/iptables.rules',
              'dsh_group': '',
              'director': 'ldirectord',
              'maintenance_dir': ''
              }
    def test_help(self):
        help_string = "# director config"
        test = lvsm.ConfigurePrompt(self.config).onecmd(' help')
        self.assertEqual(test, help_string)

if __name__ == '__main__':
    unittest.main()
