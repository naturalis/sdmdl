from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.data_prep.prediction_data import PredictionData
import unittest
import pandas as pd
import rasterio
import gdal
import numpy as np
import os


class PredictionDataTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.verbose = False

        self.cpd = PredictionData(self.gh, self.verbose)

    def test__init__(self):
        self.assertEqual(self.cpd.gh, self.gh)
        self.assertEqual(self.cpd.verbose, self.verbose)

    def test_prepare_prediction_df(self):
        lon, lat, row, col, myarray, mean_std = self.cpd.prepare_prediction_df()
        lon_truth = np.load(self.root + '/prediction_data/lon.npy')
        lat_truth = np.load(self.root + '/prediction_data/lat.npy')
        row_truth = np.load(self.root + '/prediction_data/row.npy')
        col_truth = np.load(self.root + '/prediction_data/col.npy')
        myarray_truth = gdal.Open(self.root + '/root/gis/stack/stacked_env_variables.tif').ReadAsArray()
        mean_std_truth = np.load(self.root + '/prediction_data/mean_std.npy')
        self.assertEqual(lon.tolist(), lon_truth.tolist())
        self.assertEqual(lat.tolist(), lat_truth.tolist())
        self.assertEqual(row, row_truth.tolist())
        self.assertEqual(col, col_truth.tolist())
        self.assertEqual(myarray.tolist(), myarray_truth.tolist())
        self.assertEqual(mean_std.tolist(), mean_std_truth.tolist())

    def test_create_prediction_df(self):
        os.remove(self.root + '/root/gis/world_prediction_array.npy')
        os.remove(self.root + '/root/gis/world_prediction_row_col.csv')
        self.assertFalse(os.path.isfile(self.root + '/root/gis/world_prediction_array.npy'))
        self.assertFalse(os.path.isfile(self.root + '/root/gis/world_prediction_row_col.csv'))

        self.cpd.create_prediction_df()

        self.assertTrue(os.path.isfile(self.root + '/root/gis/world_prediction_array.npy'))
        npy_result = np.load(self.root + '/root/gis/world_prediction_array.npy')
        npy_truth = np.load(self.root + '/prediction_data/world_prediction_array.npy')
        self.assertEqual(npy_result.tolist(), npy_truth.tolist())

        self.assertTrue(os.path.isfile(self.root + '/root/gis/world_prediction_row_col.csv'))
        csv_result = pd.read_csv(self.root + '/root/gis/world_prediction_row_col.csv')
        csv_truth = pd.read_csv(self.root + '/prediction_data/world_prediction_row_col.csv')
        self.assertEqual(csv_result.to_numpy().tolist(), csv_truth.to_numpy().tolist())


if __name__ == '__main__':
    unittest.main()
