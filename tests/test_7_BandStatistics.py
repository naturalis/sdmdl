from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.data_prep.band_statistics import BandStatistics
import os
import unittest
import pandas as pd


class BandStatisticsTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.verbose = False
        self.cbm = BandStatistics(self.gh, self.verbose)

    def test__init__(self):
        self.assertEqual(self.cbm.gh, self.gh)
        self.assertEqual(self.cbm.verbose, self.verbose)

    def test_calc_band_mean_and_stddev(self):

        os.remove(self.root + '/root/gis/env_bio_mean_std.txt')
        self.assertFalse(os.path.isfile(self.root + '/root/gis/env_bio_mean_std.txt'))
        self.cbm.calc_band_mean_and_stddev()
        result = pd.read_csv(self.root + '/root/gis/env_bio_mean_std.txt', delimiter='\t')
        truth = pd.read_csv(self.root + '/band_statistics/env_bio_mean_std.txt', delimiter='\t')
        self.assertTrue(os.path.isfile(self.root + '/root/gis/env_bio_mean_std.txt'))
        self.assertEqual(list(result.columns), ['band', 'mean', 'std_dev'])
        self.assertEqual(result.to_numpy().tolist(), truth.to_numpy().tolist())


if __name__ == '__main__':
    unittest.main()
