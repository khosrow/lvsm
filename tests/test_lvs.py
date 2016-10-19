import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lvsm')))


from lvsm import lvs


class GenericDirector(unittest.TestCase):
    """Testing the generic director funcationality"""
    def setUp(self):
        # for now only testing ldirectord
        self.director = lvs.Director('generic', path + '/scripts/ipvsadm')
        self.maxDiff = None

    def test_convertfilename(self):
        filename = 'localhost:http'
        expected_result = '127.0.0.1:80'
        self.assertEqual(self.director.convert_filename(filename),
                         expected_result)

    def test_show(self):
        expected_result = ["",
                           "Layer 4 Load balancing",
                           "======================",
                           "TCP  192.0.2.2:80                             rr     ",
                           "  -> 192.0.2.200:80                           Masq    1      0          0         ",
                           "",
                           "UDP  192.0.2.2:53                             rr     ",
                           "  -> 192.0.2.202:53                           Masq    1      0          0         ",
                           "  -> 192.0.2.203:53                           Masq    1      0          0         ",
                           "",
                           ""]
        result = self.director.show(True, False)
        self.assertEqual(result, expected_result)
        

if __name__ == "__main__":
    unittest.main()
