from sdmdl.sdmdl.gis_handler import gis_handler
import unittest
import os

class GisHandlerTestSuite(unittest.TestCase):

    """Test cases for Config Handler class."""

    def setUp(self):

        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data/gis_handler'

    def test__init__(self):

        self.gh = gis_handler(self.root)
        self.assertEqual(self.gh.root,self.root)
        self.assertEqual(self.gh.scaled,'')
        self.assertEqual(self.gh.non_scaled,'')
        self.assertEqual(self.gh.gis,'')
        self.assertEqual(self.gh.world_locations_to_predict,'')
        self.assertEqual(self.gh.empty_map,'')
        self.assertEqual(self.gh.variables,[])
        self.assertEqual(self.gh.names,[])
        self.assertEqual(self.gh.length,0)
        self.assertEqual(self.gh.scaled_len,0)
        self.assertEqual(self.gh.presence,'')
        self.assertEqual(self.gh.stack,'')
        self.assertEqual(self.gh.stack_clip,'')
        self.assertEqual(self.gh.spec_ppa,'')
        self.assertEqual(self.gh.spec_ppa_env,'')

    def test_validate_gis(self):
        self.gh = gis_handler(self.root)
        self.gh.validate_gis()
        self.assertEqual(self.gh.gis,self.root + '/gis')
        self.assertEqual(self.gh.scaled,self.gh.root + '/scaled')
        self.assertEqual(self.gh.non_scaled,self.gh.root + '/non-scaled')
        self.assertEqual(self.gh.world_locations_to_predict,self.root + '/world_locations_to_predict.csv')
        self.assertEqual(self.gh.empty_map,self.root + '/empty_land_map.tif')

        with self.assertRaises(IOError):
            self.gh = gis_handler(self.root + '/scaled')
            self.gh.validate_gis()

    def test_validate_list(self):
        self.gh = gis_handler(self.root)
        self.gh.validate_gis()
        f, n, = self.gh.variables_list(self.root)
        self.assertEqual(f,[self.root + x for x in ['/empty_land_map.tif','/non-scaled/ecoregion/Boreal_Forests_Taiga_map.tif','/non-scaled/ecoregion/Deserts_and_Xeric_Shrublands_map.tif','/scaled/bioclim/bio1.tif','/scaled/ecoattribute/habitat_fragmentation.tif']])
        self.assertEqual(n,['empty_land_map','Boreal_Forests_Taiga_map','Deserts_and_Xeric_Shrublands_map','bio1','habitat_fragmentation'])

    def test_validate_tif(self):
        self.gh = gis_handler(self.root)
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.assertEqual(self.gh.variables,[self.root + x for x in ['/scaled/bioclim/bio1.tif','/scaled/ecoattribute/habitat_fragmentation.tif','/non-scaled/ecoregion/Boreal_Forests_Taiga_map.tif','/non-scaled/ecoregion/Deserts_and_Xeric_Shrublands_map.tif']])
        self.assertEqual(self.gh.names,['bio1','habitat_fragmentation','Boreal_Forests_Taiga_map','Deserts_and_Xeric_Shrublands_map'])
        self.assertEqual(self.gh.length,4)
        self.assertEqual(self.gh.scaled_len,2)

        with self.assertRaises(IOError):
            self.gh = gis_handler(self.root + '/scaled')
            self.gh.validate_gis()

    def test_define_output(self):
        self.gh = gis_handler(self.root)
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.assertEqual(self.gh.presence,self.gh.non_scaled + '/presence')
        self.assertEqual(self.gh.stack, self.gh.gis + '/stack')
        self.assertEqual(self.gh.stack_clip,self.gh.gis + '/stack_clip')
        self.assertEqual(self.gh.spec_ppa, self.gh.root + '/spec_ppa')
        self.assertEqual(self.gh.spec_ppa_env,self.gh.root + '/spec_ppa_env')


if __name__ == '__main__':
    unittest.main()