from pygbif import occurrences as occ
from pygbif import species
import time
import os

def RequestArchive(name, path):

    if not os.path.exists(path):
        os.makedirs(path)
    
    sp = species.name_suggest(q=name)
    
    req = occ.download(['taxonKey = %s' % sp[0]['key'], 'hasGeospatialIssue = FALSE', 'hasCoordinate = TRUE'],pred_type = 'and' ,user = 'winand', pwd = 'Boedelhof4!', email = 'winand@live.nl')

    download = False

    while download == False:
        try:
            occ.download_get(req[0],path)
            
            meta = occ.download_meta(key = req[0])
            
            with open(path + 'DOI.csv', 'w') as f:
                for key in meta.keys():
                    f.write("%s,%s\n"%(key,meta[key]))
            download = True
            print("The DarwinArchive for %s has completed downloading." % name)
        except:
            time.sleep(15)

# RequestArchive('Zea mays subsp. mays', 'C:/Users/winan/Documents/Naturalis/Occurance Data/Crops/Zea mays subsp. mays')
