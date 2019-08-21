import sys

syspath = '/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms/script/python'

if syspath not in sys.path:
    sys.path += [syspath]

from train_model import train_model
from plot_training_results import plot_training_results

def train (path):
    
    train_model(path)
    plot_training_results(path)