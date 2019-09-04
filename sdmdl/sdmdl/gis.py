import os


class GIS:
    '''gis_handler object for managing all gis related files and objects. Additionally keeps track of any output files created and their output paths'''

    # root = config root of 'data' folder.

    def __init__(self, root):

        '''gis_handler object initiation. Recording relevant filepaths, statistics on included variables.'''

        self.root = root

        self.scaled = ''
        self.non_scaled = ''
        self.gis = ''
        self.world_locations_to_predict = ''
        self.empty_map = ''

        self.variables = []
        self.names = []
        self.length = 0
        self.scaled_len = 0

        self.presence = ''
        self.stack = ''
        self.stack_clip = ''
        self.spec_ppa = ''
        self.spec_ppa_env = ''

    def validate_gis(self):

        '''validate_gis function that validates if certain required files and locations are present.'''

        for root, dirs, files in os.walk(self.root):
            for d in dirs:
                if 'gis' == d:
                    self.gis = (root + '/' + d).replace('\\','/')
                elif 'scaled' == d:
                    self.scaled = (root + '/' + d).replace('\\','/')
                elif 'non-scaled' == d:
                    self.non_scaled = (root + '/' + d).replace('\\','/')
            for f in files:
                if 'world_locations_to_predict.csv' == f:
                    self.world_locations_to_predict = (root + '/' + f).replace('\\','/')
                elif 'empty_land_map.tif' == f:
                    self.empty_map = (root + '/' + f).replace('\\','/')

        if self.world_locations_to_predict == '' or self.empty_map == '':
            raise IOError(
                'The two required files, world_locations_to_predict.csv and/or empty_land_map.tif files are not present in the data folder.')

        self.gis = (self.root + '/gis').replace('\\','/') if self.gis == '' else self.gis.replace('\\', '/')
        self.scaled = (self.gis + '/scaled').replace('\\','/') if self.scaled == '' else self.scaled.replace('\\', '/')
        self.non_scaled = (self.gis + '/non-scaled').replace('\\','/') if self.non_scaled == '' else self.non_scaled.replace('\\', '/')

    def variables_list(self, root):

        '''creates a list of filepaths and names of .tif files corresponding to a given path.'''

        f = []
        n = []
        for a, b, c in os.walk(root):
            for file in c:
                file_ext = file.split('.')[-1]
                fx = file_ext.lower()
                if fx == 'tif' or fx == 'tiff':
                    f += [a.replace('\\', '/') + '/' + file]
                    n += [file.replace('.%s' % file_ext, '')]
        return [f, n]

    def validate_tif(self):

        '''validate_tif function that validates the available .tif files'''

        self.variables = []
        self.names = []
        self.length = 0
        self.scaled_len = 0

        variables_s, names_s = self.variables_list(self.scaled)
        variables_ns, names_ns = self.variables_list(self.non_scaled)
        self.variables = variables_s + variables_ns
        self.names = names_s + names_ns
        self.scaled_len = len(variables_s)
        self.length = len(self.variables)
        if len(self.variables) == 0 or len(self.names) == 0:
            raise IOError('no tif files are present in the scaled and non_scaled folders.')

    def define_output(self):

        '''define_output function sets a list of standard output locations for intermediate files.'''

        self.presence = (self.non_scaled + '/presence').replace('\\','/')
        self.stack = (self.gis + '/stack').replace('\\','/')
        self.stack_clip = (self.gis + '/stack_clip').replace('\\','/')
        self.spec_ppa = (self.root + '/spec_ppa').replace('\\','/')
        self.spec_ppa_env = (self.root + '/spec_ppa_env').replace('\\','/')