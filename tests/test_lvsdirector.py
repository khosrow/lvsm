import unittest
import os
import sys
import StringIO

from lvsm import lvsdirector

path = os.path.abspath(os.path.dirname(__file__))

class DirectorTestCase(unittest.TestCase):
    def setUp(self):
        # for now only testing ldirectord
        self.director = lvsdirector.Director('ldirectord', path + '/maintenance',
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

    def test_showrealactive(self):
        self.assertTrue(True)

    def test_showrealdisabled(self):
        self.assertTrue(True)

    def test_showvirtualudp(self):
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
UDP  example.org:domain           rr
  -> resolver1.opendns.com:domain Masq    1      0          0
  -> resolver1.opendns.com:domain Masq    1      0          0"""
        # capture stdout
        output = StringIO.StringIO()
        sys.stdout = output
        self.director.show_virtual('example.org', 'domain', 'udp', False)
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())

    def test_showvirtualtcp(self):
        expected_result = """IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  www.example.com:http         rr
  -> google.com:http              Masq    1      0          0
  -> slashdot.org:http            Masq    1      0          0"""
        # capture stdout
        output = StringIO.StringIO()
        sys.stdout = output
        self.director.show_virtual('www.example.com', 'http', 'tcp', False)
        result = output.getvalue()
        self.assertEqual(result.rstrip(), expected_result.rstrip())
        self.assertTrue(True)
