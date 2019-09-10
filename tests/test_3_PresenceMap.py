from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.data_prep.presence_map import PresenceMap
import numpy as np
import pandas as pd
import unittest
import rasterio
import shutil
import random
import os


class PresenceMapTestCase(unittest.TestCase):

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

        self.cpm = PresenceMap(self.oh, self.gh, self.verbose)

    def test__init__(self):
        self.assertEqual(self.cpm.oh, self.oh)
        self.assertEqual(self.cpm.gh, self.gh)
        self.assertEqual(self.cpm.verbose, self.verbose)

    def test_create_presence_map(self):
        shutil.move(self.root + '/root/gis/layers/non-scaled/presence/arachis_duranensis_presence_map.tif', self.root + '/root/gis/layers/non-scaled/presence/true_arachis_duranensis_presence_map.tif')
        shutil.move(self.root + '/root/gis/layers/non-scaled/presence/solanum_bukasovii_presence_map.tif', self.root + '/root/gis/layers/non-scaled/presence/true_solanum_bukasovii_presence_map.tif')
        self.assertFalse(os.path.isfile(self.root + '/root/gis/layers/non-scaled/presence/arachis_duranensis_presence_map.tif'))
        self.assertFalse(os.path.isfile(self.root + '/root/gis/layers/non-scaled/presence/solanum_bukasovii_presence_map.tif'))
        self.cpm.create_presence_map()
        result_a = rasterio.open(self.root + '/root/gis/layers/non-scaled/presence/arachis_duranensis_presence_map.tif')
        result_b = rasterio.open(self.root + '/root/gis/layers/non-scaled/presence/solanum_bukasovii_presence_map.tif')
        truth_a = rasterio.open(self.root + '/presence_map/arachis_duranensis_presence_map.tif')
        truth_b = rasterio.open(self.root + '/presence_map/solanum_bukasovii_presence_map.tif')
        self.assertTrue(os.path.isfile(self.root + '/root/gis/layers/non-scaled/presence/arachis_duranensis_presence_map.tif'))
        self.assertTrue(os.path.isfile(self.root + '/root/gis/layers/non-scaled/presence/solanum_bukasovii_presence_map.tif'))
        self.assertEqual(result_a.read(1).tolist(), truth_a.read(1).tolist())
        self.assertEqual(result_b.read(1).tolist(), truth_b.read(1).tolist())
        [raster.close() for raster in [result_a, result_b, truth_a, truth_b]]
        os.remove(self.root + '/root/gis/layers/non-scaled/presence/arachis_duranensis_presence_map.tif')
        os.remove(self.root + '/root/gis/layers/non-scaled/presence/solanum_bukasovii_presence_map.tif')
        shutil.move(self.root + '/root/gis/layers/non-scaled/presence/true_arachis_duranensis_presence_map.tif', self.root + '/root/gis/layers/non-scaled/presence/arachis_duranensis_presence_map.tif')
        shutil.move(self.root + '/root/gis/layers/non-scaled/presence/true_solanum_bukasovii_presence_map.tif', self.root + '/root/gis/layers/non-scaled/presence/solanum_bukasovii_presence_map.tif')

if __name__ == '__main__':
    unittest.main()
