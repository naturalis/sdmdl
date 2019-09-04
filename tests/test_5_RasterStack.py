from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS
from sdmdl.sdmdl.data_prep.raster_stack import RasterStack
import numpy as np
import unittest
import rasterio
import os


class RasterStackTestCase(unittest.TestCase):

    def setUp(self):
        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data').replace('\\', '/')
        self.gh = GIS(self.root + '/root')
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.verbose = False
        self.crs = RasterStack(self.gh, self.verbose)

    def test__init__(self):

        self.assertEqual(self.crs.gh, self.gh)

    def test_create_raster_stack(self):
        os.remove(self.root + '/root/gis/stack/stacked_env_variables.tif')
        self.assertFalse(os.path.isfile(self.root + '/root/gis/stack/stacked_env_variables.tif'))
        self.crs.create_raster_stack()
        self.assertTrue(os.path.isfile(self.root + '/root/gis/stack/stacked_env_variables.tif'))
        ra = rasterio.open(self.gh.variables[0])
        rb = rasterio.open(self.gh.variables[1])
        rc = rasterio.open(self.gh.variables[2])
        rd = rasterio.open(self.gh.variables[3])
        raster_result = rasterio.open(self.root + '/root/gis/stack/stacked_env_variables.tif')
        np.testing.assert_array_equal(ra.read(1), raster_result.read(1))
        np.testing.assert_array_equal(rb.read(1), raster_result.read(2))
        np.testing.assert_array_equal(rc.read(1), raster_result.read(3))
        np.testing.assert_array_equal(rd.read(1), raster_result.read(4))
        [raster.close() for raster in [ra, rb, rc, rd, raster_result]]


if __name__ == '__main__':
    unittest.main()
