import yaml
import io
import os


# This needs class-level documentation
class Config:
    """config_handler object that manages the config file, containing information on the data, occurrences and result
    paths. """

    def __init__(self, root, oh, gh):

        """config_handler object initiation."""

        self.root = root.replace('\\', '/')
        self.oh = oh
        self.gh = gh

        self.config = []
        self.yml_names = ['data_path', 'occurrence_path', 'result_path', 'occurrences', 'layers']

        # Why can't we pass these as **kwargs?
        self.data_path = None
        self.occ_path = None
        self.result_path = None
        self.yml = None

    # Why can we not pass the config file to the constructor?
    # This is destined to bump into another .travis.yml or
    # whatever in the future.
    def search_config(self):

        """search_config function that recursively find the location of the config.yml file."""

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

        """create_yaml function that can be used for initialization of the package (creates a new config file upon
        running the first time). """

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
               self.yml_names[4]: lay_dict}

        with io.open(self.config, 'w', encoding='utf8') as outfile:
            yaml.dump(yml, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def read_yaml(self):

        """read_yaml function that reads the config file at the previously found location and extracts all relavant
        information from it to set instance variables. """

        try:
            with open(self.config, 'r') as stream:
                self.yml = yaml.safe_load(stream)
        except:
            raise IOError('Config file found in root "%s" is corrupted, please repair the dictionary structure or '
                          'save the file with no content and create a new sdmdl object.' % self.root)

        if self.yml is None:
            self.create_yaml()
            self.read_yaml()

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
        if self.data_path == '' or self.occ_path == '':
            raise IOError('The yaml file found does not contain a path for the data and/or occurrences.')