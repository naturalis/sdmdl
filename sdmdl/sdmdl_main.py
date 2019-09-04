import os
import logging

from sdmdl.sdmdl.config import Config
from sdmdl.sdmdl.occurrences import Occurrences
from sdmdl.sdmdl.gis import GIS

from sdmdl.sdmdl.data_prep.presence_map import PresenceMap
from sdmdl.sdmdl.data_prep.raster_stack import RasterStack
from sdmdl.sdmdl.data_prep.presence_pseudo_absence import PresencePseudoAbsence
from sdmdl.sdmdl.data_prep.band_statistics import BandStatistics
from sdmdl.sdmdl.data_prep.training_data import TrainingData
from sdmdl.sdmdl.data_prep.prediction_data import PredictionData

from sdmdl.sdmdl.train_handler import train_handler

from sdmdl.sdmdl.predict_handler import predict_handler


class sdmdl:
    '''sdmdl object with one parameter: root of the repository, that is holding all occurrences and environmental layers.'''

    def __init__(self, root, dat_root='/data', occ_root='/data/occurrences'):
        '''sdmdl object initiation.'''

        self.root = root
        self.occ_root = self.root + occ_root if occ_root == '/data/occurrences' else occ_root
        self.dat_root = self.root + dat_root if dat_root == '/data' else dat_root

        self.oh = Occurrences(self.occ_root)
        self.oh.validate_occurrences()
        self.oh.species_dictionary()

        self.gh = GIS(self.dat_root)
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()

        self.ch = Config(self.dat_root, self.oh, self.gh)
        self.ch.search_config()
        self.ch.read_yaml()

        # change this later when using log4py
        self.verbose = True
        if self.verbose:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            logging.getLogger("tensorflow").setLevel(logging.ERROR)

    def reload_config(self):
        '''pass.'''

        pass

    def prep(self):
        '''prep function that manages the process of data pre-processing.'''

        cpm = PresenceMap(self.oh, self.gh, self.verbose)
        cpm.create_presence_map()

        self.gh.validate_tif()

        crs = RasterStack(self.gh, self.verbose)
        crs.create_raster_stack()

        ppa = PresencePseudoAbsence(self.oh, self.gh, self.verbose)
        ppa.create_presence_pseudo_absence()

        cbm = BandStatistics(self.gh, self.verbose)
        cbm.calc_band_mean_and_stddev()

        ctd = TrainingData(self.oh, self.gh, self.verbose)
        ctd.create_training_df()

        cpd = PredictionData(self.gh, self.verbose)
        cpd.create_prediction_df()

    def train(self):
        '''train function that manages the process of model training.'''

        th = train_handler(self.oh, self.gh, self.ch, self.verbose)
        th.train()

    def plot_performance_metric(self):
        '''pass'''

        pass

    def predict(self):
        '''predict function that manages the process of model prediction.'''

        ph = predict_handler(self.oh, self.gh, self.ch, self.verbose)
        ph.predict_model()

    def clean(self):
        '''pass.'''

        pass
        # create a function to remove all created files