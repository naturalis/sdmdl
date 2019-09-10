import os


# This class should include functionality for validating if the files can be properly imported, checking if the affine
# transformations and resolutions are compatible for stacking, so potential problems can be detected before the raster
# are imported during the data preparation.

class GIS:

    """Manages all GIS related path and file names required for computation of gis data. Additionally manages the paths
    for any output files the package creates.

    :param root: a string representation of the root of the data folder ('root/data') which should contain:
    world_locations_to_predict.csv and empty_land_map.tif

    :return: Object. Used to manage tif layers and created files.
    """

    def __init__(self, root):

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

        """Validates if certain required files and locations are present.

        :return: None. Set instance variables equal to the required file and directory paths.
        If one of the required files is not found return error.
        """

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
                'The two required files, world_locations_to_predict.csv and/or empty_land_map.tif files are not '
                'present in the data folder.')

        self.gis = (self.root + '/gis').replace('\\','/') if self.gis == '' else self.gis.replace('\\', '/')
        self.scaled = (self.gis + '/scaled').replace('\\','/') if self.scaled == '' else self.scaled.replace('\\', '/')
        self.non_scaled = (self.gis + '/non-scaled').replace('\\','/') if self.non_scaled == '' else self.non_scaled.replace('\\', '/')

    def variables_list(self, root):

        """Creates a list of file paths (f) and names (n) of raster (.tif) files that are found recursively in a given
         path.

        :param root: string representation of a file path

        :return: List. Containing:
        list 'f' containing a number of string file paths, one for each raster file found in the root;
        list 'n' containing a number of string names corresponding to the name of the raster file.
        """

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

        """Validation of raster (.tif) files present in the scaled and non-scaled directory.
        WARNING: this step currently does not verify if the input layers are compatible for the raster stack computation
        To succesfully stack the rasters make sure all tif layers (including the empty land map) have an identical
        affine transformation and resolution.

        :return: None. Set 4 instance variables:
        1. Set variables to a list of path names corresponding to all the raster layers found.
        2. Set names to a list of file names corresponding to all the raster layers found.
        3. Set scaled_len to the number of layers in the scaled folder.
        4. Set length to the total number of layers.
        """

        self.variables = []
        self.names = []
        self.length = 0
        self.scaled_len = 0

        variables_s, names_s = self.variables_list(self.scaled)
        variables_ns, names_ns = self.variables_list(self.non_scaled)
        self.variables = sorted(variables_s) + sorted(variables_ns)
        self.names = sorted(names_s) + sorted(names_ns)
        self.scaled_len = len(variables_s)
        self.length = len(self.variables)
        if len(self.variables) == 0 or len(self.names) == 0:
            raise IOError('no tif files are present in the scaled and non_scaled folders.')

    def define_output(self):

        """Set a list of standard output locations for intermediate files.

        :return: None. Set the locations of the presence, stack, stack_clip, spec_ppa and spec_ppa_env folders to
        instance variable.
        """

        self.presence = (self.non_scaled + '/presence').replace('\\','/')
        self.stack = (self.gis + '/stack').replace('\\','/')
        self.stack_clip = (self.gis + '/stack_clip').replace('\\','/')
        self.spec_ppa = (self.root + '/spec_ppa').replace('\\','/')
        self.spec_ppa_env = (self.root + '/spec_ppa_env').replace('\\','/')