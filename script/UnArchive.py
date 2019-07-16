from zipfile import ZipFile
import pandas as pd
import os

def UnArchive(ArchivePath,SpeciesName):
    root = '/'.join(ArchivePath.split('/')[0:-1])
    temp = root + '/temp/'
    with ZipFile(ArchivePath, 'r') as zipObj:
        zipObj.extractall(temp)
    data = pd.read_csv(temp + 'occurrence.txt',sep = "\t", header = False)
    data = data[['gbifID','decimalLatitude','decimalLongitude','acceptedScientificName']]
    data.to_csv('/'.join([root,SpeciesName]) + '.csv')
    for f in os.listdir('/'.join([temp,'dataset'])):
        os.remove('/'.join([temp,'dataset',f]))
    os.rmdir('/'.join([temp,'dataset']))
    for f in os.listdir(temp):
        os.remove(''.join([temp,f]))
    os.rmdir(temp)
    
# data = UnArchive('C:/Users/winan/Documents/Naturalis/Occurance Data/Crops/Zea mays subsp. mays')


