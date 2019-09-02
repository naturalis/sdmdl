from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.create_prediction_df import CreatePredictionDF
import unittest
import pandas as pd
import rasterio
import gdal
import numpy as np
import os


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.oh = occurrence_handler(self.root + '/occurrence_handler')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = gis_handler(self.root + '/gis_handler')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.ch = config_handler(self.root + '/config_handler', self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.verbose = False

        self.cpd = CreatePredictionDF(self.oh, self.gh, self.ch, self.verbose)

    def test__init__(self):
        self.assertEqual(self.cpd.oh,self.oh)
        self.assertEqual(self.cpd.gh,self.gh)
        self.assertEqual(self.cpd.ch,self.ch)
        self.assertEqual(self.cpd.verbose,self.verbose)

    def test_prepare_prediction_df(self):
        self.cpd.gh.gis = self.root + '/create_prediction_df'
        self.cpd.gh.stack = self.root + '/raster_stack_clip'
        lon, lat, row, col, myarray, mean_std = self.cpd.prep_predicion_df()
        df = pd.read_csv(self.root + '/create_prediction_df/world_locations_to_predict.csv')
        lon_truth = df["decimal_longitude"].values
        lat_truth = df["decimal_latitude"].values
        src_truth = rasterio.open(self.root + '/raster_stack_clip/stacked_env_variables.tif')
        row_truth = []
        col_truth = []
        for i in range(len(df)):
            row_n, col_n = src_truth.index(lon_truth[i], lat_truth[i])
            row_truth.append(row_n)
            col_truth.append(col_n)
        myarray_truth = gdal.Open(self.root + '/raster_stack_clip/stacked_env_variables.tif').ReadAsArray()
        mean_std_truth = pd.read_csv(self.root + '/create_prediction_df/env_bio_mean_std.txt', delimiter='\t').to_numpy()

        self.assertEqual(lon,lon_truth)
        self.assertEqual(lat,lat_truth)
        self.assertEqual(row,row_truth)
        self.assertEqual(col,col_truth)
        self.assertEqual(myarray.tolist(),myarray_truth.tolist())
        self.assertEqual(mean_std.tolist(),mean_std_truth.tolist())


    def test_create_prediction_df(self):
        self.cpd.gh.spec_ppa = self.root + '/create_presence_pseudo_absence'
        self.cpd.gh.gis = self.root + '/create_prediction_df'
        self.cpd.gh.stack = self.root + '/raster_stack_clip'
        self.assertFalse(os.path.isfile(self.root + '/create_prediction_df/world_prediction_array.npy'))
        self.assertFalse(os.path.isfile(self.root + '/create_prediction_df/world_prediction_row_col.csv'))

        self.cpd.create_prediction_df()

        self.assertTrue(os.path.isfile(self.root + '/create_prediction_df/world_prediction_array.npy'))
        npy_result = np.load(self.root + '/create_prediction_df/world_prediction_array.npy')
        npy_truth = np.load(self.root + '/create_prediction_df/world_prediction_array_truth.npy')
        self.assertEqual(npy_result.tolist(), npy_truth.tolist())
        os.remove(self.root + '/create_prediction_df/world_prediction_array.npy')

        self.assertTrue(os.path.isfile(self.root + '/create_prediction_df/world_prediction_row_col.csv'))
        csv_result = pd.read_csv(self.root + '/create_prediction_df/world_prediction_row_col.csv')
        csv_truth = pd.read_csv(self.root + '/create_prediction_df/world_prediction_row_col_truth.csv')
        self.assertEqual(csv_result.to_numpy().tolist(), csv_truth.to_numpy().tolist())
        os.remove(self.root + '/create_prediction_df/world_prediction_row_col.csv')



if __name__ == '__main__':
    unittest.main()
