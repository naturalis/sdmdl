import sys

syspath = '/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms/script/python'

if syspath not in sys.path:
    sys.path += [syspath]

from create_presence_maps import create_presence_maps
from create_raster_stack import create_raster_stack
from raster_stack_clip import raster_stack_clip
from create_presence_pseudo_absence import create_presence_pseudo_absence
from calc_band_mean_and_stddev import calc_band_mean_and_stddev
from create_env_df import create_env_df
from create_prediction_df import create_prediction_df

def prep (path):

    create_presence_maps(path)
    create_raster_stack(path)    
    raster_stack_clip(path)
    create_presence_pseudo_absence(path)
    calc_band_mean_and_stddev(path)
    create_env_df(path)
    create_prediction_df(path)