from sdmdl.read_config import read_config

from sdmdl.create_presence_maps import create_presence_maps
from sdmdl.create_raster_stack import create_raster_stack
from sdmdl.raster_stack_clip import raster_stack_clip
from sdmdl.create_presence_pseudo_absence import create_presence_pseudo_absence
from sdmdl.calc_band_mean_and_stddev import calc_band_mean_and_stddev
from sdmdl.create_env_df import create_env_df
from sdmdl.create_prediction_df import create_prediction_df

from sdmdl.train_model import train_model
from sdmdl.plot_training_results import plot_training_results

from sdmdl.predict_global_distribution import predict_global_distribution

class sdmdl():
    
    def __init__ (self,path):
        
        self.path = path
        
        _, verbose = read_config(self.path)
        
        self.verbose = verbose
        
        # add other config settings
        
    def reload (self):
        _, verbose = read_config(self.path)
        
        self.verbose = verbose 
        
        # add other config settings
        
    def prep (self):
        
        create_presence_maps(self.path)
        create_raster_stack(self.path)
        raster_stack_clip(self.path)
        create_presence_pseudo_absence(self.path)
        calc_band_mean_and_stddev(self.path)
        create_env_df(self.path)
        create_prediction_df(self.path)
               
    def train (self):
        train_model(self.path)
        
    def plot_performance_metric(self):
        plot_training_results(self.path)
        
    def predict (self):
        predict_global_distribution(self.path)
        
    def clean (self):
        pass
        # create a function to remove all created files