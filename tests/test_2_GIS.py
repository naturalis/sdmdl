from sdmdl.sdmdl.gis import GIS
import unittest
import os


class GISTesCase(unittest.TestCase):
    """Test cases for Config Handler class."""

    def setUp(self):
        self.root = (os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data/root').replace('\\',
                                                                                                           '/')

    def test__init__(self):
        self.gh = GIS(self.root)
        self.assertEqual(self.gh.root, self.root)
        self.assertEqual(self.gh.scaled, '')
        self.assertEqual(self.gh.non_scaled, '')
        self.assertEqual(self.gh.gis, '')
        self.assertEqual(self.gh.world_locations_to_predict, '')
        self.assertEqual(self.gh.empty_map, '')
        self.assertEqual(self.gh.variables, [])
        self.assertEqual(self.gh.names, [])
        self.assertEqual(self.gh.length, 0)
        self.assertEqual(self.gh.scaled_len, 0)
        self.assertEqual(self.gh.presence, '')
        self.assertEqual(self.gh.stack, '')
        self.assertEqual(self.gh.stack_clip, '')
        self.assertEqual(self.gh.spec_ppa, '')
        self.assertEqual(self.gh.spec_ppa_env, '')

    def test_validate_gis(self):
        self.gh = GIS(self.root)
        self.gh.validate_gis()
        self.assertEqual(self.gh.gis, self.root + '/gis')
        self.assertEqual(self.gh.scaled, self.gh.root + '/gis/layers/scaled')
        self.assertEqual(self.gh.non_scaled, self.gh.root + '/gis/layers/non-scaled')
        self.assertEqual(self.gh.world_locations_to_predict, self.root + '/gis/world_locations_to_predict.csv')
        self.assertEqual(self.gh.empty_map, self.root + '/gis/layers/empty_land_map.tif')

        with self.assertRaises(IOError):
            self.gh = GIS(self.root + '/scaled')
            self.gh.validate_gis()

    def test_validate_list(self):
        self.gh = GIS(self.root)
        self.gh.validate_gis()
        test_root = self.root + '/gis/layers/scaled'
        f, n, = self.gh.variables_list(test_root)
        f_truth = []
        n_truth = []
        for a, b, c in sorted(os.walk(test_root)):
            for file in c:
                file_ext = file.split('.')[-1]
                fx = file_ext.lower()
                if fx == 'tif' or fx == 'tiff':
                    f_truth += [a.replace('\\', '/') + '/' + file]
                    n_truth += [file.replace('.%s' % file_ext, '')]
        self.assertEqual(f, f_truth)
        self.assertEqual(n, n_truth)

    def test_validate_tif(self):
        self.gh = GIS(self.root)
        self.gh.validate_gis()
        self.gh.validate_tif()
        f1, n1 = self.gh.variables_list(self.root + '/gis/layers/scaled')
        f2, n2 = self.gh.variables_list(self.root + '/gis/layers/non-scaled')
        variables_truth = f1 + f2
        names_truth = n1 + n2
        self.assertEqual(self.gh.variables, variables_truth)
        self.assertEqual(self.gh.names, names_truth)
        self.assertEqual(self.gh.length, 6)
        self.assertEqual(self.gh.scaled_len, 4)

        with self.assertRaises(IOError):
            self.gh = GIS(self.root + '/scaled')
            self.gh.validate_gis()

    def test_define_output(self):
        self.gh = GIS(self.root)
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()
        self.assertEqual(self.gh.presence, (self.gh.non_scaled + '/presence'))
        self.assertEqual(self.gh.stack, (self.gh.gis + '/stack'))
        self.assertEqual(self.gh.stack_clip, (self.gh.gis + '/stack_clip'))
        self.assertEqual(self.gh.spec_ppa, (self.gh.root + '/spec_ppa'))
        self.assertEqual(self.gh.spec_ppa_env, (self.gh.root + '/spec_ppa_env'))


if __name__ == '__main__':
    unittest.main()
