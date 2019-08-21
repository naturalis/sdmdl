from zipfile import ZipFile
import pandas as pd
import os

def UnArchive(ArchivePath,SpeciesName):
    root = '/'.join(ArchivePath.split('/')[0:-1])
    temp = root + '/temp/'
    with ZipFile(ArchivePath, 'r') as zipObj:
        zipObj.extractall(temp)
    data = pd.read_csv(temp + 'occurrence.txt',sep = "\t")
    data = data[['gbifID','decimalLatitude','decimalLongitude','acceptedScientificName']]
    data.to_csv('/'.join([root,SpeciesName]) + '.csv')
    for f in os.listdir('/'.join([temp,'dataset'])):
        os.remove('/'.join([temp,'dataset',f]))
    os.rmdir('/'.join([temp,'dataset']))
    for f in os.listdir(temp):
        os.remove(''.join([temp,f]))
    os.rmdir(temp)
   
spec_list = []

for d, p ,f in os.walk('/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms/data/occurrences'):
    spec_list += [d]
    
spec_list = spec_list[1:]

name_list = []
for species in spec_list:
    name_list += [species.split('/')[-1]]

for all in range(len(spec_list)):  
    UnArchive(''.join([spec_list[all],'/',name_list[all],'.zip']),name_list[all])