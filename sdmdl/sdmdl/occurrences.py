import pandas as pd
import os

# This class currently does not check the data in the imported files. This means that if the decimalLatitude and
# decimalLongitude columns include any data type other then numerical it has the potential to crash, and similarly
# if any values are out of bounds of for the raster layer these do currently not get filtered. This means that filtering
# the input data to the model is a requirement.


class Occurrences:
    """Manages all occurrence related path and file names. Additionally manages a species dictionary containing one
    occurrence table per species.
    Take note that any tables provided need to be in either .csv or .xls format. Furthermore
    the table needs to have two required columns labeled 'decimalLatitude/decimallatitude' and
    'decimalLongitude/decimallongitude' that contain coordinates in the WGS84 coordinate system.
    WARNING: the Occurrence class currently does not filter out any incorrect data. This entails that
    loading tables with incorrect data types (strings or other categorical data) or invalid coordinates
    (outside the extent of the provided raster images) may lead to errors and crashes.

    :param root: a string representation of the root of the occurrence folder ('root/data/occurrences') which should
    contain occurrence tables.

    :return: Object. Used to manage occurrence data.
    """

    def __init__(self, root):

        self.root = root

        self.length = 0
        self.path = []
        self.name = []

        self.spec_dict = {}

    def validate_occurrences(self):

        """Validates the presence of any .csv or .xls files recursively. Additionally collects some basic statistics on
        the occurrences.

         :return: None. Sets path and name instance variables to a list of file names and species names that have been
         recursively found in self.root, also sets length instance variable to the number of species/files that have
         been found. If no files can be found returns error.
         """

        path = []
        name = []

        for root, dirs, files in os.walk(self.root):
            for file in files:
                file_ext = file.split('.')[-1]
                if file_ext == 'csv' and 'world_locations_to_predict.csv' != file:
                    table = pd.read_csv(root + '/' + file)
                elif (file_ext == 'xlsx' or file_ext == 'xls') and 'world_locations_to_predict.csv' != file:
                    table = pd.read_excel(root + '/' + file)
                else:
                    continue
                col_list = [col.lower() for col in list(table.columns)]
                if 'decimallatitude' in col_list and 'decimallongitude' in col_list:
                    self.length += 1
                    path += [(root + '/' + file).replace('\\', '/')]
                    name += [file.replace('.%s' % file_ext, '')]
                else:
                    Warning(
                        'file "%s" is missing either the "decimalLatitude" or "decimalLongitude" column and was excluded.' % file)
        if self.length == 0:
            raise IOError('no occurrences are present in the occurrences folder: %s.' % self.root)

        self.path = path
        self.name = name

    def species_dictionary(self):

        """Creates one dictionary containing one table per occurrence file found in the previous class method

        :return: None. Sets spec_dict instance variable to a species dictionary, where each key in the dictionary is a
        species name and the corresponding value is its occurrence table.
        """

        species_occ_dict = {}
        for i in range(len(self.path)):
            file_ext = self.path[i].split('.')[-1]
            if file_ext == 'csv':
                table = pd.read_csv(self.path[i])
            elif file_ext == 'xls' or file_ext == 'xlsx':
                table = pd.read_excel(self.path[i])
            col_list = [col.lower() for col in list(table.columns)]
            col_list[col_list.index('decimallongitude')] = 'dLon'
            col_list[col_list.index('decimallatitude')] = 'dLat'
            table.columns = col_list
            table = table[['dLon', 'dLat']]
            species_occ_dict["%s" % self.name[i]] = table

        self.spec_dict = species_occ_dict
