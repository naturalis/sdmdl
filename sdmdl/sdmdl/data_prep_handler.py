import pandas as pd
import rasterio
import tqdm
import os

class data_prep_handler():
    
    def __init__(self,occurrence_handler,gis_handler,verbose):
        
        self.occurrence_handler = occurrence_handler
        
        self.gis_handler = gis_handler
        
        self.verbose = verbose
        
    def create_presence_maps(self):
        
        species_occ_dict = self.occurrence_handler.species_dictionary()
    
        src=rasterio.open(self.gis_handler.empty_map)
        profile=src.profile
        band=src.read(1)
    
        if not os.path.isdir(self.gis_handler.presence):
            os.makedirs(self.gis_handler.presence,exist_ok=True)
    
        for key in (tqdm.tqdm(species_occ_dict,desc='Creating presence maps' + (28 * ' ')) if self.verbose else species_occ_dict):
            new_band = band.copy()
    
            presence_data = species_occ_dict[key]
            presence_data["present/pseudo_absent"]=1
            spec = key
            long=presence_data["dLon"]
            lati=presence_data["dLat"]
            long=pd.Series.tolist(long)
            lati=pd.Series.tolist(lati)
    
            for i in range(0,len(presence_data)):
                row,col=src.index(long[i],lati[i])
                new_band[row,col]=1
    
            with rasterio.open(self.gis_handler.presence + '/%s_presence_map.tif' % spec, 'w', **profile) as dst:
                dst.write(new_band.astype(rasterio.float32), 1)