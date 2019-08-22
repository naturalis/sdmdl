from sdmdl.sdmdl.load_taxa_list import load_taxa_list
import pandas as pd
import tqdm
import rasterio
import os

'''create_presence_maps function that uses occurrence data present in ~/data/occurrences_cleaned and creates a raster file for each species.'''

def create_presence_maps(path,verbose=True):
    
    # Access taxa list.

    taxa, species_occ_dict = load_taxa_list(path)
    
    # Load empty map to create species presence map.
    
    src=rasterio.open(path+'/data/GIS/layers/empty_land_map.tif')
    profile=src.profile
    band=src.read(1)
    
    # When presence folder does not exist create it.
    
    if not os.path.isdir(path+'/data/GIS/layers/non-scaled/presence'):
        os.makedirs(path+'/data/GIS/layers/non-scaled/presence',exist_ok=True)
    
    # Create presence map for each species.
    
    for key in (tqdm.tqdm(species_occ_dict,desc='Creating presence maps' + (28 * ' ')) if verbose else species_occ_dict):
        new_band = band.copy()
        
        # Obtain lon - lat presence points.
        
        presence_data = species_occ_dict[key]
        presence_data["present/pseudo_absent"]=1
        spec = key
        long=presence_data["decimalLongitude"]
        lati=presence_data["decimalLatitude"]
        long=pd.Series.tolist(long)
        lati=pd.Series.tolist(lati)
    
        # Set raster cell values to 100 if species is present.
        
        for i in range(0,len(presence_data)):
            row,col=src.index(long[i],lati[i])
            new_band[row,col]=1

        # Save presence map to file.
    
        with rasterio.open(path+'/data/GIS/layers/non-scaled/presence/%s_presence_map.tif'%spec, 'w', **profile) as dst:
            dst.write(new_band.astype(rasterio.float32), 1)