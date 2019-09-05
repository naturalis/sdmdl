from sdmdl.sdmdl.occurrences import Occurrences
import unittest
import pandas as pd
import os


class OccurrencesTestCase(unittest.TestCase):
    """Test cases for Occurrence class."""

    def setUp(self):
        self.root = (
                    os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data/root').replace(
            '\\', '/')

    def test__init__(self):
        self.oh = Occurrences(self.root)
        self.assertEqual(self.oh.root, self.root)
        self.assertEqual(self.oh.length, 0)
        self.assertEqual(self.oh.path, [])
        self.assertEqual(self.oh.name, [])
        self.assertEqual(self.oh.spec_dict, {})

    def test_validate_occurrences(self):
        self.oh = Occurrences(self.root)
        self.oh.validate_occurrences()
        self.assertEqual(self.oh.length, 2)
        self.assertEqual(self.oh.path, [self.root + '/occurrences/arachis_duranensis.csv', self.root + '/occurrences/solanum_bukasovii.csv'])
        self.assertEqual(self.oh.name, ['arachis_duranensis', 'solanum_bukasovii'])

    def test_species_dictionary(self):
        self.oh = Occurrences(self.root)
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.assertIsInstance(self.oh.spec_dict, dict)
        self.assertEqual(list(self.oh.spec_dict.keys()), ['arachis_duranensis', 'solanum_bukasovii'])
        self.assertEqual(list(self.oh.spec_dict['arachis_duranensis']),
                         ['dLon','dLat'])
        spec_dict_truth = pd.read_csv(self.root + '/occurrences/solanum_bukasovii.csv')[['decimalLongitude', 'decimalLatitude']]
        self.assertEqual(self.oh.spec_dict['solanum_bukasovii'].values.tolist(), spec_dict_truth.to_numpy().tolist())


if __name__ == '__main__':
    unittest.main()
