from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.band_statistics_helper import BandStatisticsHelper
import os
import unittest
import pandas as pd


class CreateBandMeanAndStddevTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.gh = gis_handler(self.root + '/gis_handler')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.verbose = False

        self.gh.stack = self.root + '/raster_stack_clip'

        self.cbm = BandStatisticsHelper(self.gh, self.verbose)

    def test__init__(self):
        self.assertEqual(self.cbm.gh,self.gh)
        self.assertEqual(self.cbm.verbose,self.verbose)

    def test_calc_band_mean_and_stddev(self):
        self.assertFalse(os.path.isfile(self.root + '/gis_handler/gis/env_bio_mean_std.txt'))
        self.cbm.calc_band_mean_and_stddev()
        result = pd.read_csv(self.root + '/gis_handler/gis/env_bio_mean_std.txt',delimiter='\t')
        truth = pd.read_csv(self.root + '/calc_band_mean_and_stddev/env_bio_mean_std.txt',delimiter='\t')
        self.assertTrue(os.path.isfile(self.root + '/gis_handler/gis/env_bio_mean_std.txt'))
        self.assertEqual(list(result.columns),['band','mean','std_dev'])
        self.assertEqual(result.to_numpy().tolist(),truth.to_numpy().tolist())
        os.remove(self.root + '/gis_handler/gis/env_bio_mean_std.txt')
        os.rmdir(self.root + '/gis_handler/gis')



if __name__ == '__main__':
    unittest.main()
