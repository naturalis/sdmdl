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

from sdmdl.sdmdl.trainer import Trainer

from sdmdl.sdmdl.predictor import Predictor


class sdmdl:

    """sdmdl object with one required parameter: root of the repository, that is holding all occurrences and
    environmental layers. And two additional parameters: dat_root (data root of raster layers) and occ_root (root of
    occurrence files.

    Note: the root of the raster layers and occurrence data can be changed. Be aware that directories provided by the
    user need to contain required files that are present on the GitHub repository.

    :param root: a string representation of the root of the cloned or copied GitHub repository.
    :param dat_root: a string representation of the data directory within the repository. Any files that are present
    in the repositories data folder also need to be present in the directory provided by the user.
    :param occ_root: a string representation of the occurrence directory within the data directory of repository.
    :return: Object. Used to manage all phases of model creation. Handling data preparations, model training and
    prediction.
    """

    def __init__(self, root, dat_root='/data', occ_root='/data/occurrences'):

        """sdmdl object initiation."""

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

        self.verbose = self.ch.verbose
        if not self.verbose:
            # used to silence tensorflow backend deprecation warnings.
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            logging.getLogger("tensorflow").setLevel(logging.ERROR)

    def reload_config(self):
        """unimplemented, required later for changes to the config file to be automatically detected."""

        pass

    def prep(self):
        """prep function that manages the process of data pre-processing."""

        cpm = PresenceMap(self.oh, self.gh, self.verbose)
        cpm.create_presence_map()

        # currently the raster layers need to be validated again to detect the new presence maps created in the previous
        # step. Adding these presence maps to the list of raster layers could be integrated into the create_presence_map
        # method of the PresenceMap class.

        # Note: This currently leads to unwanted behaviour when:
        # A new sdmdl object is created, the data is already preprocessed, and the user executes the method train
        # without first executing the method prep. This would not be a problem if raster layers were automatically
        # detected but is caused by the creation of the config.yml file that does not including the presence maps.

        self.gh.validate_tif()

        crs = RasterStack(self.gh, self.verbose)
        crs.create_raster_stack()

        ppa = PresencePseudoAbsence(self.oh, self.gh, self.ch, self.verbose)
        ppa.create_presence_pseudo_absence()

        cbm = BandStatistics(self.gh, self.verbose)
        cbm.calc_band_mean_and_stddev()

        ctd = TrainingData(self.oh, self.gh, self.verbose)
        ctd.create_training_df()

        cpd = PredictionData(self.gh, self.verbose)
        cpd.create_prediction_df()

    def train(self):
        """train function that manages the process of model training."""

        th = Trainer(self.oh, self.gh, self.ch, self.verbose)
        th.train()

    def predict(self):
        """predict function that manages the process of model prediction."""

        ph = Predictor(self.oh, self.gh, self.ch, self.verbose)
        ph.predict_model()

    def clean(self):
        """pass."""

        def listdir_if_exists(path):
            if os.path.isdir(path):
                return os.listdir(path)
            else:
                return []

        def rm_if_exists(path):
            if os.path.isfile(path):
                os.remove(path)

        def rmdir_if_exists(path):
            if os.path.isdir(path):
                os.rmdir(path)

        for f in listdir_if_exists(self.gh.non_scaled + '/presence'):
            rm_if_exists(self.gh.non_scaled + '/presence/' + f)
        rmdir_if_exists(self.gh.non_scaled + '/presence')
        rm_if_exists(self.gh.stack + '/stacked_env_variables.tif')
        rmdir_if_exists(self.gh.stack)
        for f in listdir_if_exists(self.gh.spec_ppa):
            rm_if_exists(self.gh.spec_ppa + '/' + f)
        rmdir_if_exists(self.gh.spec_ppa)
        rm_if_exists(self.gh.gis + '/env_bio_mean_std.txt')
        for f in listdir_if_exists(self.gh.spec_ppa_env):
            rm_if_exists(self.gh.spec_ppa_env + '/' + f)
        rmdir_if_exists(self.gh.spec_ppa_env)
        rm_if_exists(self.gh.gis + '/world_prediction_array.npy')
        rm_if_exists(self.gh.gis + '/world_prediction_row_col.csv')
        rm_if_exists(self.gh.root + '/filtered.csv')
