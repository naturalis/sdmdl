from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
import yaml
import unittest
import os

class ConfigTestCase(unittest.TestCase):
    """Test cases for Config Handler class."""

    def setUp(self):

        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data').replace('\\','/')
        self.oh = occurrence_handler(self.root + '/occurrence_handler')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = gis_handler(self.root + '/gis_handler')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()

    def test__init__(self):
        self.ch = config_handler(self.root + '/config_handler', self.oh, self.gh)
        self.assertEqual(self.ch.oh,self.oh)
        self.assertEqual(self.ch.gh,self.gh)
        self.assertEqual(self.ch.root, self.root + '/config_handler')

    def test_search_config(self):
        self.ch = config_handler(self.root + '/config_handler', self.oh, self.gh)
        self.ch.search_config()
        self.assertEqual(self.ch.config,self.root + '/config_handler/config.yml')
        with self.assertRaises(IOError):
            self.ch = config_handler(self.root + '/no_config', self.oh, self.gh)
            self.ch.search_config()

    def test_create_yaml(self):
        self.ch = config_handler(self.root + '/config_handler', self.oh, self.gh)
        self.ch.search_config()
        self.ch.create_yaml()
        with open(self.ch.config, 'r') as stream:
            yml = yaml.safe_load(stream)
        self.assertIsInstance(yml,dict)
        self.assertEqual(list(yml.keys()),['data_path','occurrence_path','result_path','occurrences','layers'])
        self.assertEqual(yml[list(yml.keys())[0]],self.root + '/config_handler')
        self.assertEqual(yml[list(yml.keys())[1]],self.root + '/config_handler/occurrences')
        self.assertEqual(yml[list(yml.keys())[2]],self.root + '/config_handler/results')
        self.assertEqual(yml[list(yml.keys())[3]],dict(zip(self.oh.name, self.oh.path)))
        self.assertEqual(yml[list(yml.keys())[4]],dict(zip(self.gh.names, self.gh.variables)))

    def test_read_yaml(self):
        self.ch = config_handler(self.root + '/config_handler', self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.assertEqual(self.ch.data_path,self.root + '/config_handler')
        self.assertEqual(self.ch.occ_path,self.root + '/config_handler/occurrences')
        self.assertEqual(self.ch.result_path,self.root + '/config_handler/results')
        self.assertEqual(self.ch.oh.name,list(dict(zip(self.oh.name, self.oh.path)).keys()))
        self.assertEqual(self.ch.oh.path,list(dict(zip(self.oh.name, self.oh.path)).values()))
        self.assertEqual(self.ch.gh.names,list(dict(zip(self.gh.names, self.gh.variables)).keys()))
        self.assertEqual(self.ch.gh.variables,list(dict(zip(self.gh.names, self.gh.variables)).values()))

if __name__ == '__main__':
    unittest.main()
