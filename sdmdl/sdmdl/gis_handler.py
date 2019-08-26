import os


class gis_handler():
    """manages gis related files and objects. keeps track of any output files created and their output paths"""

    # root = config root of 'data' folder.

    def __init__(self, root):

        """gis_handler object initiation. Recording relevant filepaths, statistics on included variables."""

        self.root = root
        self.world_locations_to_predict = ''
        self.empty_map = ''
        self.gis = ''
        self.scaled = ''
        self.non_scaled = ''
        self.variables = []
        self.names = []
        self.length = 0
        self.scaled_len = 0

        self.presence = ''
        self.stack = ''
        self.stack_clip = ''
        self.spec_ppa = ''
        self.spec_ppa_env = ''

        self.validate_gis()
        self.validate_tif()
        self.define_output()

    def validate_gis(self):

        """validate_gis function that validates if certain required files and locations are present."""

        for root, dirs, files in os.walk(self.root):
            for d in dirs:
                if 'scaled' == d:
                    self.scaled = root + '/' + d
                elif 'non-scaled' == d:
                    self.non_scaled = root + '/' + d
                elif 'gis' == d:
                    self.gis = root + '/' + d
            for f in files:
                if 'world_locations_to_predict.csv' == f:
                    self.world_locations_to_predict = root + '/' + f
                elif 'empty_land_map.tif' == f:
                    self.empty_map = root + '/' + f
        if self.world_locations_to_predict == '' or self.empty_map == '':
            raise IOError(
                'world_locations_to_predict.csv and/or empty_land_map.tif files are not present in the data folder.')
        if self.scaled == '' or self.non_scaled == '' or self.gis == '':
            raise IOError('scaled, non-scaled and/or gis folders are not present in the data folder.')

    def validate_tif(self):

        """validate_tif function that validates the available .tif files"""

        def variables_list(path):

            """creates a list of filepaths and names of .tif files corresponding to a given path."""

            f = []
            n = []
            for a, b, c in os.walk(path):
                for file in c:
                    file_ext = file.split('.')[-1]
                    fx = file_ext.lower()
                    if fx == 'tif' or fx == 'tiff':
                        f += [a.replace('\\', '/') + '/' + file]
                        n += [file.replace('.%s' % file_ext, '')]
            return ([f, n])

        variables_s, names_s = variables_list(self.scaled)
        variables_ns, names_ns = variables_list(self.non_scaled)
        self.variables = variables_s + variables_ns
        self.names = names_s + names_ns
        self.scaled_len = len(variables_s)
        self.length = len(self.variables)
        if len(self.variables) == 0 or len(self.names) == 0:
            raise IOError('no tif files are present in the scaled and non_scaled folders.')

    def reload_tifs(self):

        """reload_tifs updates the instance variables: self.variables, self.names and self.scaled_len"""

        self.variables = []
        self.names = []
        self.scaled_len = 0
        self.validate_tif()

    def define_output(self):

        """define_output function sets a list of standard output locations for intermediate files."""

        self.presence = self.non_scaled + '/presence'
        self.stack = self.gis + '/stack'
        self.stack_clip = self.gis + '/stack_clip'
        self.spec_ppa = self.root + '/spec_ppa'
        self.spec_ppa_env = self.root + '/spec_ppa_env'
