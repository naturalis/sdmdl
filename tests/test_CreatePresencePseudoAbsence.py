from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep.create_presence_pseudo_absence_helper import create_presence_pseudo_absence_helper
import unittest
import pandas as pd
import gdal
import ast
import os


class CreatePresencePseudoAbsenceTestCase(unittest.TestCase):

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

    def test__init__(self):
        self.gh.stack = self.root + '/raster_stack_clip'
        self.cppa = create_presence_pseudo_absence_helper(self.oh, self.gh, self.ch, self.verbose)
        self.assertEqual(self.cppa.oh,self.oh)
        self.assertEqual(self.cppa.gh,self.gh)
        self.assertEqual(self.cppa.ch,self.ch)
        self.assertEqual(self.cppa.verbose,self.verbose)
        self.assertEqual(self.cppa.random_sample_size, 0)
        self.assertEqual(self.cppa.spec,'')
        self.assertEqual(self.cppa.outer_random_sample_lon_lats,[])
        self.assertEqual(self.cppa.stack_path,self.gh.stack + '/stacked_env_variables.tif')

    def test_draw_random_absence(self):
        self.gh.stack = self.root + '/raster_stack_clip'
        self.cppa = create_presence_pseudo_absence_helper(self.oh, self.gh, self.ch, self.verbose)
        self.cppa.key = 'testspecies1'
        self.cppa.draw_random_absence()
        with open(self.root + '/ppa.txt', 'r') as f:
            l = f.read()
            l = ast.literal_eval(l)
        self.assertEqual(self.cppa.outer_random_sample_lon_lats.tolist(),l)

    def test_create_ppa_df(self):
        self.gh.stack = self.root + '/raster_stack_clip'
        self.cppa = create_presence_pseudo_absence_helper(self.oh, self.gh, self.ch, self.verbose)
        self.cppa.key = 'testspecies1'
        presence_map = self.cppa.draw_random_absence()
        self.cppa.spec = self.cppa.key
        self.cppa.random_sample_size = 2000
        self.cppa.create_ppa_df(presence_map)
        table_result = pd.read_csv(self.root + '/gis_handler/spec_ppa/testspecies1_ppa_dataframe.csv')
        table_true = pd.read_csv(self.root + '/create_presence_pseudo_absence/testspecies1_ppa_dataframe.csv')
        self.assertTrue(table_result.values.tolist(),table_true.values.tolist())
        os.remove(self.root + '/gis_handler/spec_ppa/testspecies1_ppa_dataframe.csv')
        os.rmdir(self.root + '/gis_handler/spec_ppa')

    def test_create_presence_pseudo_absence(self):
        self.assertFalse(os.path.isdir(self.gh.spec_ppa))
        self.assertFalse(os.path.isfile(self.gh.spec_ppa + '/testspecies1_ppa_dataframe.csv'))
        self.assertFalse(os.path.isfile(self.gh.spec_ppa + '/testspecies2_ppa_dataframe.csv'))
        self.gh.stack = self.root + '/raster_stack_clip'
        self.cppa = create_presence_pseudo_absence_helper(self.oh, self.gh, self.ch, self.verbose)
        self.cppa.create_presence_pseudo_absence()
        self.assertTrue(os.path.isdir(self.gh.spec_ppa))
        self.assertTrue(os.path.isfile(self.gh.spec_ppa + '/testspecies1_ppa_dataframe.csv'))
        self.assertTrue(os.path.isfile(self.gh.spec_ppa + '/testspecies2_ppa_dataframe.csv'))
        os.remove(self.root + '/gis_handler/spec_ppa/testspecies1_ppa_dataframe.csv')
        os.remove(self.root + '/gis_handler/spec_ppa/testspecies2_ppa_dataframe.csv')
        os.rmdir(self.root + '/gis_handler/spec_ppa')




if __name__ == '__main__':
    unittest.main()
