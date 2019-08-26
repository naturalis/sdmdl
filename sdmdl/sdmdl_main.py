import os
import logging

from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.data_prep_handler import data_prep_handler
from sdmdl.sdmdl.train_handler import train_handler
from sdmdl.sdmdl.predict_handler import predict_handler

class sdmdl:
    
    '''sdmdl object with one parameter: root of the repository, that is holding all occurrences and environmental layers.'''
    
    def __init__ (self,root):
        
        '''sdmdl object initiation.'''
        
        self.root = root        
        self.ch = config_handler(root)        
        self.oh = occurrence_handler(self.ch.occ_path)        
        self.gh = gis_handler(self.ch.data_path)
           
        # change this later when using log4py  
        self.verbose = True       
        if self.verbose:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            logging.getLogger("tensorflow").setLevel(logging.ERROR)    
        
    def reload_config (self):
        
        '''pass.'''
        
        pass
        
    def prep (self):

        '''prep function that manages the process of data pre-processing.'''
        
        dph = data_prep_handler(self.oh,self.gh,self.ch,self.verbose)
        dph.create_presence_maps()  
        self.gh.reload_tifs()
        dph.create_raster_stack()
        dph.raster_stack_clip()
        dph.create_presence_pseudo_absence()
        dph.calc_band_mean_and_stddev()
        dph.create_training_df()
        dph.create_prediction_df()      
        
    def train (self):
        
        '''train function that manages the process of model training.'''
        
        th = train_handler(self.oh,self.gh,self.ch,self.verbose)
        th.train_model()
        
    def plot_performance_metric(self):
        
        '''pass'''
        
        pass
        
    def predict (self):
        
        '''predict function that manages the process of model prediction.'''
        
        ph = predict_handler(self.oh,self.gh,self.ch,self.verbose)
        ph.predict_model()
        
    def clean (self):
        
        '''pass.'''
        
        pass
        # create a function to remove all created files