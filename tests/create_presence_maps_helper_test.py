from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.create_presence_maps_helper import create_presence_maps_helper
import numpy as np
import pandas as pd
import unittest
import rasterio
import random
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
        self.ch = config_handler(self.root + '/config_handler',self.oh,self.gh)
        self.ch.search_config()
        self.ch.read_yaml()
        self.verbose = False

    def test__init__(self):
        self.cpm = create_presence_maps_helper(self.oh,self.gh,self.ch,self.verbose)
        self.assertEqual(self.cpm.oh,self.oh)
        self.assertEqual(self.cpm.gh,self.gh)
        self.assertEqual(self.cpm.ch,self.ch)
        self.assertEqual(self.cpm.verbose,self.verbose)

    def test_open_band(self):
        self.cpm = create_presence_maps_helper(self.oh, self.gh, self.ch, self.verbose)
        src, profile, new_band = self.cpm.open_band()
        self.assertEqual(profile,rasterio.open(self.gh.empty_map).profile)
        np.testing.assert_array_equal(new_band,rasterio.open(self.gh.empty_map).read(1))

    def test_confirm_existance(self):
        self.cpm = create_presence_maps_helper(self.oh, self.gh, self.ch, self.verbose)
        self.assertFalse(os.path.isdir(self.gh.presence))
        self.cpm.confirm_existance()
        self.assertTrue(os.path.isdir(self.gh.presence))
        os.rmdir(self.gh.presence)

    def test_extract_lat_lon(self):
        self.cpm = create_presence_maps_helper(self.oh, self.gh, self.ch, self.verbose)
        presence_data, lon, lat = self.cpm.extract_lat_lon('testspecies1')
        pd.testing.assert_frame_equal(presence_data,self.oh.spec_dict['testspecies1'])
        self.assertEqual(lon,pd.Series.tolist(self.oh.spec_dict['testspecies1']['dLon']))
        self.assertEqual(lat,pd.Series.tolist(self.oh.spec_dict['testspecies1']['dLat']))
        presence_data, lon, lat = self.cpm.extract_lat_lon('testspecies2')
        pd.testing.assert_frame_equal(presence_data, self.oh.spec_dict['testspecies2'])
        self.assertEqual(lon, pd.Series.tolist(self.oh.spec_dict['testspecies2']['dLon']))
        self.assertEqual(lat, pd.Series.tolist(self.oh.spec_dict['testspecies2']['dLat']))

    def test_convert_spatial_to_image(self):
        self.cpm = create_presence_maps_helper(self.oh, self.gh, self.ch, self.verbose)
        src, profile, new_band = self.cpm.open_band()
        presence_data, lon, lat = self.cpm.extract_lat_lon('testspecies1')
        presence_data = presence_data.append(pd.DataFrame([[1,2,3,10,80,6,1],[1,2,3,-14,26,6,1],[1,2,3,44,-143,6,1],[1,2,3,12,0,6,1]],columns=list(presence_data.columns)))
        lat = pd.Series.tolist(presence_data['dLat'])
        lon = pd.Series.tolist(presence_data['dLon'])
        new_band = self.cpm.convert_spatial_to_image(presence_data,src,lat,lon,new_band)
        coords = [[1032,2220],[960,3120],[1248,2472],[552,444],[936,2160]]
        self.assertEqual(self.cpm.map_coords,coords)
        for i in range(len(coords)):
            location = new_band[self.cpm.map_coords[i][0],self.cpm.map_coords[i][1]]
            self.assertEqual(location,1.0)
        Lat = []
        Lon = []
        for i in range(0, 100):
            x = random.randint(0, 1799)
            y = random.randint(0, 4319)
            Lat.append(x)
            Lon.append(y)
        for i in range(0,100):
            if [Lat[i],Lon[i]] not in coords:
                location = new_band[Lat[i]][Lon[i]]
                self.assertTrue(location != 1.0)

if __name__ == '__main__':
    unittest.main()
