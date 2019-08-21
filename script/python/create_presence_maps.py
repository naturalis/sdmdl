import pandas as pd
import rasterio
import os

# create_presence_maps function that uses occurrence data present in ~/data/occurrences_cleaned and creates a raster file for each species.

def create_presence_maps(path):
    
# Access taxa list.
    
    taxa=pd.read_csv(path+"/data/occurrences_cleaned/taxalist.txt",header=None)
    taxa.columns=["taxon"]
       
    species_occ_dict={}
    
    for i in taxa["taxon"]:
        taxon_data = pd.read_csv(path+"/data/occurrences_cleaned/%s.csv"%i)
        
        # Add species dataframe to dictionary.
        
        species_occ_dict["%s"%i] = taxon_data  
    
    # Check whether all species have been included in the dictionary.
    
    if len(species_occ_dict.keys())==len(taxa["taxon"]):
        print("All species dataframes now in dictionary")
    else:
        print("Error: not all species dataframe included")
    
    # Load empty map to create species presence map.
    
    src=rasterio.open(path+'/data/GIS/layers/empty_land_map.tif')
    profile=src.profile
    band=src.read(1)
    
    # When presence folder does not exist create it.
    
    if not os.path.isdir(path+'/data/GIS/layers/non-scaled/presence'):
        os.makedirs(path+'/data/GIS/layers/non-scaled/presence',exist_ok=True)
    
    # Create presence map for each species.
    
    for key in species_occ_dict:
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