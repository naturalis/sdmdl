import os
import logging

from sdmdl.sdmdl.data_prep.createpresencemaphelper import CreatePresenceMapHelper
from sdmdl.sdmdl.data_prep.create_raster_stack_helper import create_raster_stack_helper
from sdmdl.sdmdl.data_prep.raster_stack_clip_helper import raster_stack_clip_helper
from sdmdl.sdmdl.data_prep.create_presence_pseudo_absence_helper import create_presence_pseudo_absence_helper
from sdmdl.sdmdl.data_prep.calc_band_mean_and_stddev import CalcBandMeanAndStddev
from sdmdl.sdmdl.data_prep.create_training_df import CreateTrainingDF
from sdmdl.sdmdl.data_prep.create_prediction_df import CreatePredictionDF

from sdmdl.sdmdl.config_handler import config_handler
from sdmdl.sdmdl.occurrence_handler import occurrence_handler
from sdmdl.sdmdl.gis_handler import gis_handler
from sdmdl.sdmdl.train_handler import train_handler
from sdmdl.sdmdl.predict_handler import predict_handler


class sdmdl:
    '''sdmdl object with one parameter: root of the repository, that is holding all occurrences and environmental layers.'''

    def __init__(self, root, dat_root='/data', occ_root='/data/occurrences'):
        '''sdmdl object initiation.'''

        self.root = root
        self.occ_root = self.root + occ_root if occ_root == '/data/occurrences' else occ_root
        self.dat_root = self.root + dat_root if dat_root == '/data' else dat_root

        self.oh = occurrence_handler(self.occ_root)
        self.oh.validate_occurrences()
        self.oh.species_dictionary()

        self.gh = gis_handler(self.dat_root)
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()

        self.ch = config_handler(self.dat_root, self.oh, self.gh)
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

        cpm = CreatePresenceMapHelper(self.oh, self.gh, self.ch, self.verbose)
        cpm.create_presence_maps()

        self.gh.validate_tif()

        crs = create_raster_stack_helper(self.oh, self.gh, self.ch, self.verbose)
        crs.create_raster_stack()

        rsc = raster_stack_clip_helper(self.oh, self.gh, self.ch, self.verbose)
        rsc.raster_stack_clip()

        ppa = create_presence_pseudo_absence_helper(self.oh, self.gh, self.ch, self.verbose)
        ppa.create_presence_pseudo_absence()

        cbm = CalcBandMeanAndStddev(self.oh, self.gh, self.ch, self.verbose)
        cbm.calc_band_mean_and_stddev()

        ctd = CreateTrainingDF(self.oh, self.gh, self.ch, self.verbose)
        ctd.create_training_df()

        cpd = CreatePredictionDF(self.oh, self.gh, self.ch, self.verbose)
        cpd.create_prediction_df()

    def train(self):
        '''train function that manages the process of model training.'''

        th = train_handler(self.oh, self.gh, self.ch, self.verbose)
        th.train_model()

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