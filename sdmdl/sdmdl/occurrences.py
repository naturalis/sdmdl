import pandas as pd
import os


class Occurrences:
    '''occurrence_handler object that manages the occurrence species and files.'''

    # root = config root of 'occurrences' folder.

    def __init__(self, root):

        '''occurrence_handler object initiation.'''

        self.root = root

        self.length = 0
        self.path = []
        self.name = []

        self.spec_dict = {}

    def validate_occurrences(self):

        '''validate_occurrences function that validates the presence of any .csv or .xls files. Additionally collects some basic statistics on the occurrences.'''

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
                    # potentially add message that file has been ignored (due to incompatible file extension).
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

        '''species_dictionary function that creates one dictionary containing all the found occurrence species.'''

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

            species_occ_dict["%s" % self.name[i]] = table

        self.spec_dict = species_occ_dict