from load_taxa_list import load_taxa_list
from import_variable_list import import_variable_list
import pandas as pd
import numpy as np
import rasterio
import gdal
import os

def create_env_df (path): 
    
    taxa, _ = load_taxa_list(path)
    
    var_names,scaled_len,var_len = import_variable_list(path)
    
    src=rasterio.open(path+'/data/GIS/stack/stacked_env_variables.tif')
    inRas=gdal.Open(path+'/data/GIS/stack/stacked_env_variables.tif')
    
    for i in taxa["taxon"][:]:
        
        data = pd.read_csv(path+"/data/spec_ppa/%s_ppa_dataframe.csv"%i)
        spec = data["taxon_name"][0]
        spec = spec.replace(" ","_")
        print("processing species ", spec)
        
    
        #get all collumn and row numbers 
        len_pd=np.arange(len(data))
        long=data["decimalLongitude"]
        lati=data["decimalLatitude"]
        ppa=data["present/pseudo_absent"]
    
        lon=long.values
        lat=lati.values
    
        row=[]
        col=[]
    
        for i in len_pd:
            row_n, col_n = src.index(lon[i], lat[i])# spatial --> image coordinates
            row.append(row_n)
            col.append(col_n)
    
        ##opening raster as 3d numpy array
        myarray=inRas.ReadAsArray()
    
        #collect file with mean and std_dev for each band
        mean_std=pd.read_csv(path+'/data/GIS/env_bio_mean_std.txt',sep="\t")
        mean_std=mean_std.to_numpy()
    
    
        ########################################################
        #extract the values for all bands and prepare input data
        ########################################################
        X=[]
        species =["%s"%spec]*int(len(row))
    
        for j in range(0,var_len):
            band=myarray[j]
            x=[]
    
          #extract coastal outline  
            
            for i in range(0,len(row)):
                value= band[row[i],col[i]]
                if j < scaled_len:
                    if value <-1000:
                        value=np.nan
                    else:  
                        value = ((value - mean_std.item((j,1))) / mean_std.item((j,2)))#scale values
                    x.append(value)
                    
                if j >= scaled_len:
                    if value <-1000:
                        value=np.nan
                    else:  
                        value=value
                    x.append(value)
            X.append(x)
        
        
    
        #set as numpy 2d array
        X =np.array([np.array(xi) for xi in X])
        #X
        
        #transform into dataframe and include row and column values
        df=pd.DataFrame(X) 
        df=df.T
        
        df["present/pseudo_absent"]=ppa
        df["decimalLatitude"]=lati
        df["decimalLongitude"]=long
        df["taxon_name"]=species
        df["present/pseudo_absent"]=ppa
        df["row_n"]=row
        df.rename(columns=dict(zip(df.columns[0:var_len], var_names)),inplace=True)
        
        #drop any potential rows with no-data values
        df=df.dropna(axis=0, how='any')
        input_data=df
        
        # When stack folder does not exist create it.
    
        if not os.path.isdir(path+'/data/spec_ppa_env'):
            os.makedirs(path+'/data/spec_ppa_env',exist_ok=True)
        
        ##save input dataframe
        input_data.to_csv(path +"/data/spec_ppa_env/%s_env_dataframe.csv"%spec)