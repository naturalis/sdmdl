from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.predictor import Predictor
import unittest
import numpy as np
import rasterio
import gdal
import os


class PredictorTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.oh = Occurrences(self.root + '/root')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.ch = Config(self.root, self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.verbose = False
        self.p = Predictor(self.oh, self.gh, self.ch, self.verbose)

    def test__init__(self):
        self.assertEqual(self.p.oh, self.oh)
        self.assertEqual(self.p.gh, self.gh)
        self.assertEqual(self.p.ch, self.ch)
        self.assertEqual(self.p.verbose, self.verbose)

    def test_prep_prediction_data(self):
        myarray, index_minb1 = self.p.prep_prediction_data()
        myarray_truth = gdal.Open(self.root + '/root/gis/stack/stacked_env_variables.tif').ReadAsArray()
        empty_map = rasterio.open(self.root + '/root/gis/layers/empty_land_map.tif')
        empty_map = empty_map.read(1)
        min_empty_map = np.min(empty_map)
        index_minb1_truth = np.where(empty_map == min_empty_map)
        self.assertEqual(myarray.tolist(), myarray_truth.tolist())
        index_minb1 = [x.tolist() for x in index_minb1]
        index_minb1_truth = [x.tolist() for x in index_minb1_truth]
        self.assertEqual(index_minb1, index_minb1_truth)

    def test_predict_distribution(self):
        myarray, index_minb1 = self.p.prep_prediction_data()
        new_band = self.p.predict_distribution(self.oh.name[0], myarray, index_minb1)
        with np.load(self.root + '/predictor/new_band.npz') as data:
            new_band_truth = data[list(data.keys())[0]]
            np.testing.assert_array_equal(new_band, new_band_truth)


if __name__ == '__main__':
    unittest.main()
