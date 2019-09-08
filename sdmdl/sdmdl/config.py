import yaml
import io
import os


class Config:

    """config object that manages the input from and output to the config file which contains settings for:
    (gis)data path,
    occurrence path,
    result path,
    occurrences (species),
    (environmental) layers,
    random seed,
    number of sampled absences,
    number of epochs,
    number of layers in model,
    nodes per layer and
    dropout per layer.
    Note: to overwrite config.yml with defaults, please open the file, delete its contents and save it under the same
    name.

    :param root: a string representation of the root of the data folder ('root/data') as it contains the config.yml
    :param oh: an Occurrence object: holds occurrence files and tables
    :param gh: a GIS object: holds path and file names required for permutation of gis data.

    :return: Object. Used to manage config.yml and the settings within it.
     """

    def __init__(self, root, oh, gh):

        self.root = root.replace('\\', '/')
        self.oh = oh
        self.gh = gh

        self.config = []
        self.yml_names = ['data_path', 'occurrence_path', 'result_path', 'occurrences', 'layers', 'random_seed',
                          'pseudo_freq', 'batchsize', 'epoch', 'model_layers', 'model_dropout']

        # Why can't we pass these as **kwargs?
        self.data_path = None
        self.occ_path = None
        self.result_path = None
        self.yml = None

        self.random_seed = 0
        self.pseudo_freq = 0
        self.batchsize = 0
        self.epoch = 0
        self.model_layers = []
        self.model_dropout = []

    # Why can we not pass the config file to the constructor?
    # This is destined to bump into another .travis.yml or
    # whatever in the future.
    def search_config(self):

        """Recursively find the location of config.yml in self.root.

        :return: None. Sets self.config equal to the file path.
        If no config is found returns error, if multiple files containing the word 'config' are found
        returns error.
        """

        for root, dirs, files in os.walk(self.root):
            for file in files:
                file_ext = file.split('.')[-1].lower()
                if (file_ext == 'yml' or file_ext == 'yaml') and 'config' in file:
                    self.config += [root + '/' + file]
        if not self.config:
            raise IOError('No yaml file found in root "%s" nor any of its subdirectories' % self.root)
        if len(self.config) != 1:
            raise IOError('Multiple yaml files found in root "%s" and its subdirectories.')
        self.config = self.config[0]

    def create_yaml(self):

        """initialization of the config file with default values (if an empty yaml file is detected while trying to
        read config.yml).

        :return: None. Overwrites empty config.yml with default values for each setting.
        """

        if len(self.oh.name) > 1:
            occ_dict = dict(zip(self.oh.name, self.oh.path))
        else:
            occ_dict = {self.oh.name[0]: self.oh.path[0]}
        if len(self.gh.names) > 1:
            lay_dict = dict(zip(self.gh.names, self.gh.variables))
        else:
            lay_dict = {self.gh.names[0]: self.gh.path[0]}

        yml = {self.yml_names[0]: self.root,
               self.yml_names[1]: self.root + '/occurrences',
               self.yml_names[2]: self.root + '/results',
               self.yml_names[3]: occ_dict,
               self.yml_names[4]: lay_dict,
               self.yml_names[5]: 42,
               self.yml_names[6]: 2000,
               self.yml_names[7]: 75,
               self.yml_names[8]: 150,
               self.yml_names[9]: [250, 200, 150, 100],
               self.yml_names[10]: [0.3, 0.5, 0.3, 0.5]}

        with io.open(self.config, 'w', encoding='utf8') as outfile:
            yaml.dump(yml, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def read_yaml(self):

        """read the config file at the previously found location and extracts all relevant
        information from it to instance variables.

        :return: None. Sets all instance variables to the values found within the config (dictionary) file.
        If config.yml can not be read return error, if config.yml is not a dictionary return error

        """

        try:
            with open(self.config, 'r') as stream:
                self.yml = yaml.safe_load(stream)
        except:
            raise IOError(
                'Config file found in root "%s" is corrupted and could not be read, please save the file with '
                'no content and create a new sdmdl object to reset it.' % self.root)

        if self.yml is None:
            self.create_yaml()
            self.read_yaml()

        if not isinstance(self.yml, dict):
            raise IOError(
                'Config file found in root "%s" is not a dictionary, please save the file with '
                'no content and create a new sdmdl object to reset it.' % self.root)

        for k in self.yml.keys():
            if self.yml_names[0] == k and not k.startswith('#'):
                self.data_path = self.yml[k]
            elif self.yml_names[1] == k and not k.startswith('#'):
                self.occ_path = self.yml[k]
            elif self.yml_names[2] == k and not k.startswith('#'):
                self.result_path = self.yml[k]
            elif self.yml_names[3] == k and not k.startswith('#'):
                self.oh.name = list(self.yml[k].keys())
                self.oh.path = list(self.yml[k].values())
            elif self.yml_names[4] == k and not k.startswith('#'):
                self.gh.names = list(self.yml[k].keys())
                self.gh.variables = list(self.yml[k].values())
            elif self.yml_names[5] == k and not k.startswith('#'):
                self.random_seed = self.yml[k]
            elif self.yml_names[6] == k and not k.startswith('#'):
                self.pseudo_freq = self.yml[k]
            elif self.yml_names[7] == k and not k.startswith('#'):
                self.batchsize = self.yml[k]
            elif self.yml_names[8] == k and not k.startswith('#'):
                self.epoch = self.yml[k]
            elif self.yml_names[9] == k and not k.startswith('#'):
                self.model_layers = self.yml[k]
            elif self.yml_names[10] == k and not k.startswith('#'):
                self.model_dropout = self.yml[k]
        if self.data_path == '' or self.occ_path == '':
            raise IOError('The yaml file found does not contain a path for the data and/or occurrences.')
