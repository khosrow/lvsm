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
        

if __name__ == "__main__":
    unittest.main()
