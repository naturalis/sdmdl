from import_variable_list import import_variable_list
import pandas as pd
import numpy as np
import rasterio
import gdal


def create_prediction_df (path):
    
    var_names,scaled_len,var_len = import_variable_list(path)
    
    ##opening raster as 3d numpy array
    inRas=gdal.Open(path+'/data/GIS/stack/stacked_env_variables.tif')
    myarray=inRas.ReadAsArray()
    print(myarray.shape)
    print(type(myarray))
    
    #get all collumn and row values for all cells to predict over 
    df=pd.read_csv(path+'/data/GIS/world_locations_to_predict.csv')
    
    len_pd=np.arange(len(df))
    lon=df["decimal_longitude"]
    lat=df["decimal_latitude"]
    lon=lon.values
    lat=lat.values
    
    row=[]
    col=[]
    
    src=rasterio.open(path+'/data/GIS/stack/stacked_env_variables.tif')
    
    for i in len_pd:
        row_n, col_n = src.index(lon[i], lat[i])# spatial --> image coordinates
        row.append(row_n)
        col.append(col_n)
    
    #collect file with mean and std_dev for each band
    mean_std=pd.read_csv(path+'/data/GIS/env_bio_mean_std.txt',sep="\t")
    mean_std=mean_std.to_numpy()
    
    
    ###########################################################
    # extract the values for all bands and prepare input data #
    ###########################################################
    X=[]
    
    for j in range(0,var_len):
        print(j)
        band=myarray[j]
        x=[]
    
        for i in range(0,len(row)):
            if j < scaled_len:
                value= band[row[i],col[i]]
                value = ((value - mean_std.item((j,1))) / mean_std.item((j,2)))#scale values
                x.append(value)
            if j >= scaled_len:
                value= band[row[i],col[i]]
                x.append(value)
        X.append(x)
    
    
    #include row and column values
    X.append(row)
    X.append(col)
        
    #set as numpy 2d array
    X =np.array([np.array(xi) for xi in X])
        
    df=pd.DataFrame(X)
        
    df=df.T
    df.rename(columns=dict(zip(df.columns[0:var_len], var_names)),inplace=True)
    df=df.dropna(axis=0, how='any')
    df.head()
        
    input_X=df.iloc[:,0:var_len]
    np.shape(input_X)
        
    row=df[var_len]
    col=df[var_len+1]
        
    row_col=pd.DataFrame({"row":row,"col":col})
        
        #convert dataframe back to numpy array
    input_X=input_X.values
        
        #convert rows and col indices back to array
    row=row.values
    col=col.values
        
        #save
    np.save(path+'/data/GIS/world_prediction_array.npy',input_X)
    row_col.to_csv(path+'/data/GIS/world_prediction_row_col.csv')