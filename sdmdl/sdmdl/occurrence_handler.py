import pandas as pd
import warnings
import os

class occurrence_handler():
    
    # root = config root of 'occurrences'
    
    def __init__(self,root):
        
        self.root = root
        self.length = 0
        self.path = []
        self.name = []
        
        self.validate_occurrences()
        
        self.spec_dict = self.species_dictionary()
    
    def validate_occurrences(self):
        for root, dirs, files in os.walk(self.root):
            for file in files:
                file_ext = file.split('.')[-1]                
                if file_ext == 'csv':
                    table = pd.read_csv(root + '/' + file)
                elif file_ext == 'xlsx' or file_ext == 'xls':
                    table = pd.read_excel(root + '/' + file)
                else:
                    # potentially add message that file has been ignored (due to incompatible file extension).
                    continue
                col_list = [col.lower() for col in list(table.columns)]
                if 'decimallatitude' in col_list and 'decimallongitude' in col_list:
                    self.length += 1
                    self.path += [root + '/' + file]
                    self.name += [file.replace('.%s' % file_ext,'')]
                else:
                    warnings.warn("file '%s' is missing either the 'decimalLatitude' or 'decimalLongitude' column and was excluded." % file)
                    
        if self.length == 0:
            raise IOError("no occurrences are present in the occurrences folder: %s." % self.root)
        
    def species_dictionary(self):
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
            species_occ_dict["%s"%self.name[i]] = table
        return(species_occ_dict)