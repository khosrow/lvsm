import unittest
import os
import sys
import StringIO

path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../lvsm')))


from lvsm.modules import keepalived


class Keepalived(unittest.TestCase):
    """Tests for the functionality of the keepalived module"""
    def setUp(self):
        args = {'keepalived-mib': 'KEEPALIVED-MIB',
                'snmp_community': 'private',
                'snmp_host': 'localhost',
                'snmp_user': '',
                'snmp_password': '',
                'cache_dir': path + '/cache'
                }
        self.director = keepalived.Keepalived(path + '/scripts/ipvsadm2',
                                              path + '/etc/keepalived.conf',
                                              restart_cmd='',
                                              nodes='',
                                              args=args)
    def teaDown(self):
        filepath1 = self.director.cache_dir + '/realServerWeight.1.1'
        filepath2 = self.director.cache_dir + '/realServerReason.1.1'
        try:
            os.unlink(filepath1)
            os.unlink(filepath2)
        except OSError:
            pass 

    def test_show_real_disabled1(self):
        # Test show_real_disabled when there's no output
        expected_result = []
        result = self.director.show_real_disabled('','',numeric=True)
        self.assertEqual(result, expected_result)

    def test_show_real_disabled2(self):
        # test when there's at least one host disabled
        output = StringIO.StringIO()
        sys.stdout = output

        # create a dummy file to trigger the host to be disabled
        filepath1 = self.director.cache_dir + '/realServerWeight.1.1'
        filepath2 = self.director.cache_dir + '/realServerReason.1.1'
        try:
            # create the file before we continue
            f = open(filepath1, 'w')
            f.write('1')
            f.close()

            f = open(filepath2, 'w')
            f.write('test')
            f.close()
    
            expected_result = ['192.0.2.200:80\t\tReason: test']
            result = self.director.show_real_disabled('','',numeric=True)
            self.assertEqual(result, expected_result)
        except IOError:
            pass
 
if __name__ == "__main__":
    unittest.main()
