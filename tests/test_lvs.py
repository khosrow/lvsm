import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lvsm')))


from lvsm import lvs
from lvsm.modules import ldirectord


class GenericDirector(unittest.TestCase):
    """Testing the generic director funcationality"""
    def setUp(self):
        # for now only testing ldirectord
        self.director = lvs.Director('generic', path + '/scripts/ipvsadm')
        self.maxDiff = None

    def test_convertfilename(self):
        filename = 'slashdot.org:http'
        expected_result = '216.34.181.45:80'
        self.assertEqual(self.director.convert_filename(filename),
                         expected_result)

    def test_show(self):
        expected_result = ["",
                           "Layer 4 Load balancing",
                           "======================",
                           "TCP  dinsdale.python.org:http                 rr     ",
                           "  -> slashdot.org:http                        Masq    1      0          0         ",
                           "",
                           "UDP  dinsdale.python.org:domain               rr     ",
                           "  -> resolver1.opendns.com:domain             Masq    1      0          0         ",
                           "  -> resolver2.opendns.com:domain             Masq    1      0          0         ",
                           "",
                           ""]
        result = self.director.show(False, False)
        self.assertEqual(result, expected_result)
        

class Ldirectord(unittest.TestCase):
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

    def test_parseconfig(self):
        configfile = path + '/etc/ldirectord.conf-1'
        self.assertTrue(self.director.parse_config(configfile))


class Keepalived(unittest.TestCase):
    def setUp(self):
        self.director = lvs.Director('keepalived',
                                     path + '/maintenance',
                                     path + '/scripts/ipvsadm',
                                     path + '/etc/keepalived.conf')

    def test_parseconfig(self):
        configfile = path + '/etc/keepalived.conf'
        self.assertTrue(self.director.parse_config(configfile))

if __name__ == "__main__":
    unittest.main()
