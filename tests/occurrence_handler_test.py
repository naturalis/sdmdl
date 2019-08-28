from sdmdl.sdmdl.occurrence_handler import occurrence_handler
import unittest
import os

class OccurrenceHandlerTestSuite(unittest.TestCase):
    
    """Test cases for Config Handler class."""

    def setUp(self):
        
        self.root = os.path.abspath(os.path.join(os.path.dirname(__file__))) + '/test_data/occurrence_handler'      
        
    def test__init__(self):

        self.oh = occurrence_handler(self.root)  
        self.assertEqual(self.oh.root,self.root)
        self.assertEqual(self.oh.length,0)
        self.assertEqual(self.oh.path,[])
        self.assertEqual(self.oh.name,[])
        self.assertEqual(self.oh.spec_dict,{})

    def test_validate_occurrences(self):
        
        self.oh = occurrence_handler(self.root) 
        self.oh.validate_occurrences()
        self.assertEqual(self.oh.length,2)
        self.assertEqual(self.oh.path,[self.root + '/testspecies1.csv',self.root + '/testspecies2.csv'])
        self.assertEqual(self.oh.name,['testspecies1','testspecies2'])
        
    def test_species_dictionary(self):
        
        self.oh = occurrence_handler(self.root) 
        self.oh.validate_occurrences()
        self.oh.species_dictionary()
        self.assertIsInstance(self.oh.spec_dict,dict)
        self.assertEqual(list(self.oh.spec_dict.keys()),['testspecies1','testspecies2'])
        self.assertEqual(list(self.oh.spec_dict['testspecies1']),['unnamed: 0', 'x', 'gbifid', 'dLat', 'dLon', 'acceptedscientificname'])
        self.assertEqual(self.oh.spec_dict['testspecies2'].values.tolist()[0],[11, 22, 33, 44, 55, 66])

if __name__ == '__main__':
    unittest.main()