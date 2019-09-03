from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.training_data_helper import CreateTrainingDF
import unittest
import pandas as pd
import os
import rasterio
import gdal


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
        self.ch = Config(self.root + '/config_handler', self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.verbose = False

        self.ctd = CreateTrainingDF(self.oh, self.gh, self.ch, self.verbose)

    def test__init__(self):
        self.assertEqual(self.ctd.oh,self.oh)
        self.assertEqual(self.ctd.gh,self.gh)
        self.assertEqual(self.ctd.ch,self.ch)
        self.assertEqual(self.ctd.verbose,self.verbose)

    def test_prep_training_df(self):
        src = rasterio.open(self.root + '/raster_stack_clip/stacked_env_variables.tif')
        inRas = gdal.Open(self.root + '/raster_stack_clip/stacked_env_variables.tif')
        self.ctd.gh.spec_ppa = self.root + '/create_presence_pseudo_absence'
        self.ctd.gh.gis = self.root + '/calc_band_mean_and_stddev'
        spec, ppa, long, lati, row, col, myarray, mean_std = self.ctd.prep_training_df(src,inRas,'testspecies1')
        ppa_truth = pd.read_csv(self.root + '/create_presence_pseudo_absence/testspecies1_ppa_dataframe.csv')
        self.assertEqual(spec,'testspecies1')
        self.assertEqual(ppa.to_numpy().tolist(),ppa_truth['present/pseudo_absent'].to_numpy().tolist())
        self.assertEqual(long.tolist(),ppa_truth['dLon'].values.tolist())
        self.assertEqual(lati.tolist(),ppa_truth['dLat'].values.tolist())
        row_t, col_t = [],[]
        for i in range(len(ppa_truth)):
            row_n, col_n = src.index(ppa_truth['dLon'].values[i], ppa_truth['dLat'].values[i])
            row_t.append(row_n)
            col_t.append(col_n)
        self.assertEqual(row,row_t)
        self.assertEqual(col,col_t)
        self.assertEqual(myarray.tolist(),inRas.ReadAsArray().tolist())
        mean_std_truth = pd.read_csv(self.root + '/calc_band_mean_and_stddev/env_bio_mean_std.txt',delimiter='\t')
        self.assertEqual(mean_std.tolist(),mean_std_truth.to_numpy().tolist())

    def test_create_training_df(self):
        self.ctd.oh.name = ['testspecies1']
        self.ctd.gh.spec_ppa = self.root + '/create_presence_pseudo_absence'
        self.ctd.gh.gis = self.root + '/calc_band_mean_and_stddev'
        self.ctd.gh.stack = self.root + '/raster_stack_clip'
        self.assertFalse(os.path.isfile(self.root + '/gis_handler/spec_ppa_env/testspecies1_env_dataframe.csv'))
        self.ctd.create_training_df()
        self.assertTrue(os.path.isfile(self.root + '/gis_handler/spec_ppa_env/testspecies1_env_dataframe.csv'))
        result = pd.read_csv(self.root + '/gis_handler/spec_ppa_env/testspecies1_env_dataframe.csv')
        truth = pd.read_csv(self.root + '/create_training_df/testspecies1_env_dataframe.csv')
        self.assertEqual(list(result.columns),list(truth.columns))
        self.assertEqual(result.to_numpy().tolist(),truth.to_numpy().tolist())
        os.remove(self.root + '/gis_handler/spec_ppa_env/testspecies1_env_dataframe.csv')
        os.rmdir(self.root + '/gis_handler/spec_ppa_env/')

if __name__ == '__main__':
    unittest.main()
