from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.data_prep.presence_pseudo_absence import PresencePseudoAbsence
import unittest
import numpy as np
import pandas as pd
import ast
import os


class PresencePseudoAbsenceTestCase(unittest.TestCase):

    def setUp(self):
        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data').replace('\\', '/')
        self.oh = Occurrences(self.root + '/root')
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.verbose = False

        self.ppa = PresencePseudoAbsence(self.oh, self.gh, self.verbose)

    def test__init__(self):

        self.assertEqual(self.ppa.oh, self.oh)
        self.assertEqual(self.ppa.gh, self.gh)
        self.assertEqual(self.ppa.verbose, self.verbose)
        self.assertEqual(self.ppa.random_sample_size, 2000)

    def test_draw_random_absence(self):
        key = 'arachis_duranensis'
        presence_data, outer_random_sample_lon_lats = self.ppa.draw_random_absence(key)
        presence_truth = np.load(self.root + '/presence_pseudo_absence/presence_data.npy',allow_pickle=True)
        outer_random_sample_lon_lats_truth = np.load(self.root + '/presence_pseudo_absence/outer_random_sample.npy')
        self.assertEqual(presence_data.to_numpy().tolist(), presence_truth.tolist())
        self.assertEqual(outer_random_sample_lon_lats.tolist(), outer_random_sample_lon_lats_truth.tolist())

    def test_create_presence_pseudo_absence(self):
        os.remove(self.root + '/root/spec_ppa/arachis_duranensis_ppa_dataframe.csv')
        os.remove(self.root + '/root/spec_ppa/solanum_bukasovii_ppa_dataframe.csv')
        self.assertFalse(os.path.isfile(self.root + '/root/spec_ppa/arachis_duranensis_ppa_dataframe.csv'))
        self.assertFalse(os.path.isfile(self.root + '/root/spec_ppa/solanum_bukasovii_ppa_dataframe.csv'))
        self.ppa.create_presence_pseudo_absence()
        self.assertTrue(os.path.isfile(self.root + '/root/spec_ppa/arachis_duranensis_ppa_dataframe.csv'))
        self.assertTrue(os.path.isfile(self.root + '/root/spec_ppa/solanum_bukasovii_ppa_dataframe.csv'))
        ppa_a = pd.read_csv(self.root + '/root/spec_ppa/arachis_duranensis_ppa_dataframe.csv')
        ppa_b = pd.read_csv(self.root + '/root/spec_ppa/solanum_bukasovii_ppa_dataframe.csv')
        truth_a = pd.read_csv(self.root + '/presence_pseudo_absence/arachis_duranensis_ppa_dataframe.csv')
        truth_b = pd.read_csv(self.root + '/presence_pseudo_absence/solanum_bukasovii_ppa_dataframe.csv')
        self.assertEqual(ppa_a.to_numpy().tolist(), truth_a.to_numpy().tolist())
        self.assertEqual(ppa_b.to_numpy().tolist(), truth_b.to_numpy().tolist())


if __name__ == '__main__':
    unittest.main()
