from sdmdl.train_model import train_model
from sdmdl.plot_training_results import plot_training_results

def train (path):
    
    train_model(path)
    plot_training_results(path)