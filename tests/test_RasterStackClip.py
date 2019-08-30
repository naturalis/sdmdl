from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.raster_stack_clip_helper import raster_stack_clip_helper
from shapely.geometry import Polygon, MultiPolygon, Point
import geopandas as gpd
import pandas as pd
import unittest
import json
import os


class RasterStackClipTestCase(unittest.TestCase):

    def setUp(self):
        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data').replace('\\', '/')
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
        self.rsc = raster_stack_clip_helper(self.oh, self.gh, self.ch, self.verbose)

    def test__init__(self):
        self.assertEqual(self.rsc.oh, self.oh)
        self.assertEqual(self.rsc.gh, self.gh)
        self.assertEqual(self.rsc.ch, self.ch)
        self.assertEqual(self.rsc.verbose, self.verbose)

    def test_disc_on_globe(self):
        points = pd.DataFrame([[0, 0], [90, 0], [0, 180], [52, 6]], columns=['dLat', 'dLon'])
        radius = 1000000
        point = [points.iloc[i] for i in range(len(points))]
        geometry = [self.rsc.disk_on_globe(p, radius) for p in point]
        geometry_str = [gpd.GeoSeries([geom]).to_json() for geom in geometry]
        f = open(self.root + '/geometries.txt', "r")
        txt = f.read()
        lines = txt.split('\n')
        for each in range(len(geometry_str)):
            self.assertEqual(geometry_str[each], lines[each])

    def test_disc_on_globe(self):
        points = pd.DataFrame([[0, 0], [90, 0], [0, 180], [52, 6]], columns=['dLat', 'dLon'])
        radius = 1000000
        multi_poly = self.rsc.buff_on_globe(points, radius)
        f = open(self.root + '/geometries.txt', "r")
        txt = f.read()
        lines = txt.split('\n')
        jso = [json.loads('%s' % l) for l in lines]
        geometries = [gpd.GeoDataFrame.from_features(js["features"]).geometry[0] for js in jso]
        geom_list = []
        self.assertIsInstance(geometries[0], Polygon)
        self.assertIsInstance(geometries[1], Polygon)
        self.assertIsInstance(geometries[2], MultiPolygon)
        self.assertIsInstance(geometries[3], Polygon)
        for geo in geometries:
            if isinstance(geo, Polygon):
                geom_list += [geo]
            elif isinstance(geo, MultiPolygon):
                for g in geo:
                    geom_list += [g]
        true_poly = MultiPolygon(geom_list)
        self.assertTrue(multi_poly.almost_equals(true_poly,0.0000001))
        f.close()

    def test_path_exists(self):
        self.assertFalse(os.path.isdir(self.gh.stack_clip))
        self.rsc.path_exists()
        self.assertTrue(os.path.isdir(self.gh.stack_clip))
        os.rmdir(self.gh.stack_clip)

    def test_data_to_spatial(self):
        self.rsc.data = pd.DataFrame([[1, 11], [-24, 2], [3, -93], [84, 4], [45, 5]], columns=['dLat', 'dLon'])
        self.rsc.data_to_spatial()
        outcome = pd.DataFrame([[1, 11], [-24, 2], [3, -93], [84, 4], [45, 5]], columns=['dLat', 'dLon'])
        outcome['coordinates'] = list(zip(outcome['dLon'], outcome['dLat']))
        outcome['coordinates'] = outcome['coordinates'].apply(Point)
        outcome['present/pseudo_absent'] = 1
        self.assertEqual(self.rsc.data.values.tolist(), outcome.values.tolist())
        self.assertEqual(list(self.rsc.data.columns), ['dLat', 'dLon', 'coordinates', 'present/pseudo_absent'])

if __name__ == '__main__':
    unittest.main()
