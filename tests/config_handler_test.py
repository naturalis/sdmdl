from sdmdl.sdmdl.config_handler import config_handler
import unittest


class ConfigHandlerTestSuite(unittest.TestCase):
    
    """Test cases for Config Handler class."""

    def setUp(self):
        self.root = '/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms'
        self.config = config_handler(self.root)
        
    def test_instance_variables(self):
        self.assertEqual(self.config.root, self.root)
        self.assertEqual(self.config.config, self.root + '/config.yml')
        self.assertEqual(self.config.data_path, self.root + '/data')
        self.assertEqual(self.config.occ_path, self.root + '/data/occurrences')
        self.assertEqual(self.config.result_path, self.root + '/results')
        
    def test_search_config(self):
        self.config.root = self.root + '/test'
        with self.assertRaises(IOError):
            self.config.search_config()
        self.config.root = self.root
        self.config.search_config()
        self.assertEqual(self.config.config,self.root + '/config.yml')
        
    def test_read_yaml(self):
        self.config.config = self.root + '/test/config.yml'
        print(self.config.config)
        with self.assertRaises(IOError):
            self.config.read_yaml()
        self.config.config = self.root + '/config.yml'
        self.config.read_yaml()
        self.assertEqual(self.config.data_path,self.root + '/data')
        self.assertEqual(self.config.occ_path,self.root + '/data/occurrences')
        self.assertEqual(self.config.result_path,self.root + '/results')

if __name__ == '__main__':
    unittest.main()