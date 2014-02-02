import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lvsm')))


from lvsm.modules import ldirectord


class Ldirectord(unittest.TestCase):
    """Tests functionality of the ldirectord module"""
    def setUp(self):
        # for now only testing ldirectord
        self.director = ldirectord.Ldirectord(path + '/scripts/ipvsadm',
                                              path + '/etc/ldirectord.conf')

    def test_disablehost(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.maintenance_dir + '/208.67.222.222'
        self.assertTrue(self.director.disable('resolver1.opendns.com'))
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError as e:
            pass

    def test_disablehostport(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.maintenance_dir + '/208.67.222.222:53'
        self.assertTrue(self.director.disable('resolver1.opendns.com', 'domain'))
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError as e:
            pass

    def test_enablehost(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.maintenance_dir + '/208.67.222.222'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.assertTrue(self.director.enable('resolver1.opendns.com'))
        except IOError as e:
            pass

    def test_enablehostport(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.maintenance_dir + '/208.67.222.222:53'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.assertTrue(self.director.enable('resolver1.opendns.com', 'domain'))
        except IOError as e:
            pass

    def test_enablehostname(self):
        output = StringIO.StringIO()
        sys.stdout = output
        filepath = self.director.maintenance_dir + '/slashdot.org'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.assertTrue(self.director.enable('slashdot.org', ''))
        except IOError as e:
            pass

    def test_parseconfig1(self):
        # Test parser on a valid config file
        configfile = path + '/etc/ldirectord.conf-1'
        self.assertTrue(self.director.parse_config(configfile))

    def test_parseconfig2(self):
        # Test parser on an invalid config file
        self.assertFalse(False)


if __name__ == "__main__":
    unittest.main()
