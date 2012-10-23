import unittest
import os
import sys
import StringIO
from lvsm import lvsdirector

path = os.path.abspath(os.path.dirname(__file__))


class DirectorTestCase(unittest.TestCase):
    def setUp(self):
        # for now only testing ldirectord
        self.director = lvsdirector.Director('ldirectord',
                                             path + '/maintenance',
                                             path + '/scripts/ipvsadm')

    def test_disablehost(self):
        filepath = self.director.maintenance_dir + '/192.0.43.10'
        self.assertTrue(self.director.disable('example.com'))
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError as e:
            pass

    def test_disablehostport(self):
        filepath = self.director.maintenance_dir + '/192.0.43.10:443'
        self.assertTrue(self.director.disable('example.com', 'https'))
        # now clean up the file
        try:
            os.unlink(filepath)
        except OSError as e:
            pass

    def test_enablehost(self):
        filepath = self.director.maintenance_dir + '/192.0.43.10'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.assertTrue(self.director.enable('example.com'))
        except IOError as e:
            pass

    def test_enablehostport(self):
        filepath = self.director.maintenance_dir + '/192.0.43.10:80'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.assertTrue(self.director.enable('example.com', 'http'))
        except IOError as e:
            pass

    def test_enablehostname(self):
        filepath = self.director.maintenance_dir + '/slashdot.org'
        try:
            # create the file before we continue
            f = open(filepath, 'w')
            f.close()
            self.assertTrue(self.director.enable('slashdot.org', ''))
        except IOError as e:
            pass

    def test_convertfilename(self):
        filename = 'slashdot.org:http'
        expected_result = '216.34.181.45:80'
        self.assertEqual(self.director.convert_filename(filename),
                         expected_result)
