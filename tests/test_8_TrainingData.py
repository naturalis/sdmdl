from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.data_prep.training_data import TrainingData
import unittest
import pandas as pd
import numpy as np
import os
import rasterio
import gdal


class TrainingDataTestCase(unittest.TestCase):

    def setUp(self):
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data'
        self.oh = Occurrences(self.root + '/root')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.verbose = False

        self.ctd = TrainingData(self.oh, self.gh, self.verbose)

    def test__init__(self):
        self.assertEqual(self.ctd.oh, self.oh)
        self.assertEqual(self.ctd.gh, self.gh)
        self.assertEqual(self.ctd.verbose, self.verbose)

    def test_prep_training_df(self):
        src = rasterio.open(self.root + '/root/gis/stack/stacked_env_variables.tif')
        inRas = gdal.Open(self.root + '/root/gis/stack/stacked_env_variables.tif')
        spec, ppa, long, lati, row, col, myarray, mean_std = self.ctd.prep_training_df(src, inRas, self.oh.name[0])
        ppa_truth = np.load(self.root + '/training_data/ppa.npy')
        long_truth = np.load(self.root + '/training_data/long.npy')
        lati_truth = np.load(self.root + '/training_data/lati.npy')
        row_truth = np.load(self.root + '/training_data/row.npy')
        col_truth = np.load(self.root + '/training_data/col.npy')
        mean_std_truth = np.load(self.root + '/training_data/mean_std.npy')
        self.assertEqual(spec, self.oh.name[0])
        self.assertEqual(ppa.to_numpy().tolist(), ppa_truth.tolist())
        self.assertEqual(long.tolist(), long_truth.tolist())
        self.assertEqual(lati.tolist(), lati_truth.tolist())
        self.assertEqual(row, row_truth.tolist())
        self.assertEqual(col, col_truth.tolist())
        self.assertEqual(myarray.tolist(), inRas.ReadAsArray().tolist())
        self.assertEqual(mean_std.tolist(), mean_std_truth.tolist())
        src.close()

    def test_create_training_df(self):
        os.remove(self.root + '/root/spec_ppa_env/arachis_duranensis_env_dataframe.csv')
        os.remove(self.root + '/root/spec_ppa_env/solanum_bukasovii_env_dataframe.csv')
        self.assertFalse(os.path.isfile(self.root + '/root/spec_ppa_env/arachis_duranensis_env_dataframe.csv'))
        self.assertFalse(os.path.isfile(self.root + '/root/spec_ppa_env/solanum_bukasovii_env_dataframe.csv'))
        self.ctd.create_training_df()
        self.assertTrue(os.path.isfile(self.root + '/root/spec_ppa_env/arachis_duranensis_env_dataframe.csv'))
        self.assertTrue(os.path.isfile(self.root + '/root/spec_ppa_env/solanum_bukasovii_env_dataframe.csv'))
        result_a = pd.read_csv(self.root + '/root/spec_ppa_env/arachis_duranensis_env_dataframe.csv')
        result_b = pd.read_csv(self.root + '/root/spec_ppa_env/solanum_bukasovii_env_dataframe.csv')
        truth_a = pd.read_csv(self.root + '/training_data/arachis_duranensis_env_dataframe.csv')
        truth_b = pd.read_csv(self.root + '/training_data/solanum_bukasovii_env_dataframe.csv')
        self.assertEqual(list(result_a.columns), list(truth_a.columns))
        self.assertEqual(list(result_a.columns), list(truth_a.columns))
        self.assertEqual(result_a.to_numpy().tolist(), truth_a.to_numpy().tolist())
        self.assertEqual(result_b.to_numpy().tolist(), truth_b.to_numpy().tolist())


if __name__ == '__main__':
    unittest.main()
