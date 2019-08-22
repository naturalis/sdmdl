from sdmdl.sdmdl.load_taxa_list import load_taxa_list
import pandas as pd
import numpy as np
import rasterio
import tqdm
import gdal
import os

def create_presence_pseudo_absence (path,verbose = True):    

    _,species_occ_dict = load_taxa_list(path)
    
    stack_path=path+'/data/GIS/stack/stacked_env_variables.tif'
    r2=gdal.Open(stack_path)

    # For each species in dictionary.    
    
    for key in (tqdm.tqdm(species_occ_dict,desc='Sampling pseudo absence' + (27 * ' ')) if verbose else species_occ_dict): 
        
        # Extract longitude and latitude of occurrence locations and label them as present (1)
        
        presence_data = species_occ_dict[key]
        presence_data["present/pseudo_absent"]=1
        spec = key
        
        long=presence_data["decimalLongitude"]
        lati=presence_data["decimalLatitude"]
        long=pd.Series.tolist(long)
        lati=pd.Series.tolist(lati)
       
        # Read raster.
        
        src=rasterio.open(stack_path)
        array=src.read_masks(1)
        
        # Set raster cell mask values of presence locations to threshold value (=1) to exclude them from pseudo-absence sampling.
        
        for i in range(0,len(presence_data)):
            row,col=src.index(long[i],lati[i])
            array[row,col]=1
        
        # Subset of cells with datavalues from which to sample pseudo-absences.
        
        (y_index_2, x_index_2) = np.nonzero(array > 1) 
        
        # Sample random locations from raster excluding sea and presence cells.
        
        r = r2
        (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = r.GetGeoTransform()        
        x_coords = x_index_2 * x_size + upper_left_x + (x_size / 2)
        y_coords = y_index_2 * y_size + upper_left_y + (y_size / 2)
        lon_lat_array=np.stack((x_coords,y_coords)).T
    
        # Determine number of pseudo-absences to sample. (POTENTIALLY CHANGE THIS!!!).
        
        random_sample_size=0
        len_p=int(len(presence_data))        
        if len_p > 2000:
            random_sample_size=len_p
        else: 
            random_sample_size=2000       
        outer_random_sample_lon_lats=lon_lat_array[np.random.choice(lon_lat_array.shape[0], random_sample_size, replace=False), :] ##
        #print(len(outer_random_sample_lon_lats), "number of outer pseudo absences")
                 
        # Add selected cells to dataset.
        
        lon=[]
        lat=[]
        psa=[0]*(random_sample_size)
        taxon=["%s"%spec]*(random_sample_size)
        gbif=["no_id"]*(random_sample_size)
    
        for item in outer_random_sample_lon_lats:
            longitude=item[0]
            latitude=item[1]
            lon.append(longitude)
            lat.append(latitude)
            
        #Dataset including occurrences and pseudo-absence points
        new_data=pd.DataFrame({"gbif_id": gbif,"taxon_name":taxon,"decimalLongitude": lon, "decimalLatitude":lat, "present/pseudo_absent": psa})
        data=pd.concat([presence_data,new_data],ignore_index=True,sort=True)
        data=data[['taxon_name','gbif_id','decimalLongitude','decimalLatitude','present/pseudo_absent']]
        data["taxon_name"]=spec
        data["row_n"]=np.arange(len(data))
         
        long=data["decimalLongitude"]
        lati=data["decimalLatitude"]
        long=pd.Series.tolist(long)
        lati=pd.Series.tolist(lati)
        
        #print(len(data),"lenght data with pseudo absences pre-filtering")
        
        #read raster
        src=rasterio.open(stack_path)
        array=src.read_masks(1)
        
            # When stack folder does not exist create it.
    
        if not os.path.isdir(path+'/data/spec_ppa'):
            os.makedirs(path+'/data/spec_ppa',exist_ok=True)
        
        data=data.reset_index(drop=True)
        data.to_csv(path + "/data/spec_ppa/%s_ppa_dataframe.csv"%spec)