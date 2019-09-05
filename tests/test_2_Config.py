from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
import yaml
import unittest
import os


class ConfigTestCase(unittest.TestCase):
    """Test cases for Config Handler class."""

    def setUp(self):
        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data').replace('\\', '/')
        self.oh = Occurrences(self.root + '/root')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()

        self.ch = Config(self.root + '/root', self.oh, self.gh)

    def test__init__(self):
        self.assertEqual(self.ch.oh, self.oh)
        self.assertEqual(self.ch.gh, self.gh)
        self.assertEqual(self.ch.root, self.root + '/root')
        self.assertEqual(self.ch.config, [])
        self.assertEqual(self.ch.yml_names, ['data_path', 'occurrence_path', 'result_path', 'occurrences', 'layers', 'random_seed', 'pseudo_freq'])
        self.assertEqual(self.ch.data_path, None)
        self.assertEqual(self.ch.occ_path, None)
        self.assertEqual(self.ch.result_path, None)
        self.assertEqual(self.ch.yml, None)
        self.assertEqual(self.ch.random_seed, 0)
        self.assertEqual(self.ch.pseudo_freq, 0)

    def test_search_config(self):
        self.ch.search_config()
        self.assertEqual(self.ch.config, self.root + '/root/config.yml')
        with self.assertRaises(IOError):
            self.ch = Config(self.root + '/config', self.oh, self.gh)
            self.ch.search_config()

    def test_create_yaml(self):
        self.ch.search_config()
        self.ch.config = self.root + '/root/test_config.yml'
        self.ch.create_yaml()
        with open(self.ch.config, 'r') as stream:
            yml = yaml.safe_load(stream)
        self.assertEqual(yml[list(yml.keys())[0]], self.root + '/root')
        self.assertEqual(yml[list(yml.keys())[1]], self.root + '/root/occurrences')
        self.assertEqual(yml[list(yml.keys())[2]], self.root + '/root/results')
        self.assertEqual(yml[list(yml.keys())[3]], dict(zip(self.oh.name, self.oh.path)))
        self.assertEqual(yml[list(yml.keys())[4]], dict(zip(self.gh.names, self.gh.variables)))
        self.assertEqual(yml[list(yml.keys())[5]], 42)
        self.assertEqual(yml[list(yml.keys())[6]], 2000)
        os.remove(self.root + '/root/test_config.yml')

    def test_read_yaml(self):
        self.ch.search_config()
        self.ch.read_yaml()
        self.assertEqual(self.ch.data_path, self.root + '/root')
        self.assertEqual(self.ch.occ_path, self.root + '/root/occurrences')
        self.assertEqual(self.ch.result_path, self.root + '/root/results')
        self.assertEqual(self.ch.oh.name, list(dict(zip(self.oh.name, self.oh.path)).keys()))
        self.assertEqual(self.ch.oh.path, list(dict(zip(self.oh.name, self.oh.path)).values()))
        self.assertEqual(self.ch.gh.names, list(dict(zip(self.gh.names, self.gh.variables)).keys()))
        self.assertEqual(self.ch.gh.variables, list(dict(zip(self.gh.names, self.gh.variables)).values()))
        self.assertEqual(self.ch.random_seed, 42)


if __name__ == '__main__':
    unittest.main()
