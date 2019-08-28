import yaml
import io
import os


class config_handler():
    '''config_handler object that manages the config file, containing information on the data, occurrences and result paths.'''

    def __init__(self, root, oh, gh):

        '''config_handler object initiation.'''

        self.oh = oh
        self.oh.validate_occurrences()
        self.oh.species_dictionary()

        self.gh = gh
        self.gh.validate_gis()
        self.gh.validate_tif()
        self.gh.define_output()

        self.root = root

        self.config = ''

    def search_config(self):

        '''search_config function that recursively find the location of the config.yml file.'''

        self.config = ''

        for root, dirs, files in os.walk(self.root):
            for file in files:
                file_ext = file.split('.')[-1].lower()
                if file_ext == 'yml' or file_ext == 'yaml':
                    self.config = root + '/' + file
        if self.config == '':
            raise IOError('No yaml file found in root "%s" nor any of its subdirectories' % self.root)

    def create_yaml(self):

        '''create_yaml function that can be used for initialization of the package (creates a new config file upon running the first time).'''

        yml = {'data_path': self.root + '/data',
               'occurrence_path': self.root + '/data/occurrences',
               'result_path': self.root + '/results',
               'occurrences': dict(zip(self.oh.name, self.oh.path)),
               'layers': dict(zip(self.gh.names, self.gh.variables))}

        with io.open(self.config, 'w', encoding='utf8') as outfile:
            yaml.dump(yml, outfile, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def read_yaml(self):

        '''read_yaml function that reads the config file at the previously found location and extracts all relavant information from it to set instance variables.'''

        try:
            with open(self.config, 'r') as stream:
                yml = yaml.safe_load(stream)
        except:
            raise IOError('Config file found in root "%s" is corrupted, please repair the file or save the file with no content.' % self.root)

        if yml == None:
            self.create_yaml()
            self.read_yaml()

        for k in yml.keys():
            if 'data_path' == k and not k.startswith('#'):
                self.data_path = yml[k]
            elif 'occurrence_path' == k and not k.startswith('#'):
                self.occ_path = yml[k]
            elif 'result_path' == k and not k.startswith('#'):
                self.result_path = yml[k]
            elif 'occurrences' == k and not k.startswith('#'):
                self.oh.name = list(yml[k].keys())
                self.oh.path = list(yml[k].values())
            elif 'layers' == k and not k.startswith('#'):
                self.gh.names = list(yml[k].keys())
                self.gh.variables = list(yml[k].values())
        if self.data_path == '' or self.occ_path == '':
            raise IOError('The yaml file found does not contain a path for the data and/or occurrences.')
