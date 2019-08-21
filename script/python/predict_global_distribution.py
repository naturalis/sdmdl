from mpl_toolkits.axes_grid1 import make_axes_locatable
from import_variable_list import import_variable_list
from load_taxa_list import load_taxa_list
from keras.models import model_from_json
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import numpy as np
import rasterio
import gdal

def predict_global_distribution (path):
        
    np.random.seed(42)
    
    var_names, _, _ = import_variable_list(path)

    taxa, _ = load_taxa_list(path)
    
    ##opening raster as 3d numpy array
    inRas=gdal.Open(path+'/data/GIS/stack/stacked_env_variables.tif')
    myarray=inRas.ReadAsArray()
    print(myarray.shape)
    print(type(myarray))
    
    #create colormap for maps
    norm = matplotlib.colors.Normalize(0,1)
    colors = [[norm(0), "0.95"],
              [norm(0.05),"steelblue"],
              [norm(0.1),"sienna"],
              [norm(0.3),"wheat"],
              [norm(0.5),"cornsilk"],
              [norm(0.95),"yellowgreen"],
              [norm(1.0),"green"]]
            
    custom_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
    custom_cmap.set_bad(color="white")
    
    fig, ax=plt.subplots()
    x = np.arange(10)
    y = np.linspace(-1,1,10)
    sc = ax.scatter(x,y, c=y, norm=norm, cmap=custom_cmap)
    fig.colorbar(sc, orientation="horizontal")
    plt.show()
    
    ###create an index of the continental borders and coastal, lake cells that should be excluded from prediction
    ### Aspect and clay percentage raster have high resolution outline 
    src=rasterio.open(path+'/data/GIS/layers/empty_land_map.tif')
    b=src.read(1)
    minb=np.min(b)
    index_minb1=np.where(b==minb)
    
    for species in taxa[:]["taxon"]:
    
        spec=species
        print("processing", spec)
        spec_index=var_names.index("%s presence map.tif"%spec.replace('_',' ')) #to later remove species own occurrences from prediction array
        print(spec_index)
    
        ##########################################################
        #  reconstruct the model and run the prediction globally #
        ##########################################################
    
        input_X=np.load(path+'/data/GIS/world_prediction_array.npy')#%spec)
        
        np.shape(input_X)
        
        #remove values for variable target species presence map based on index
        input_X=np.delete(input_X,[spec_index],1)
        np.shape(input_X)
        
        #create copy of band to later subset values in
        new_band=myarray[1].copy()
        new_band.shape
    
    
        ### Load DNN model for the species and predict values:
        json_file = open(path+'/results/{}/{}_model.json'.format(spec,spec),'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
    
        #load weights into new model
        loaded_model.load_weights(path+'/results/{}/{}_model.h5'.format(spec,spec))
    
        #compile model
        loaded_model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.001), metrics=['accuracy'])
    
        #predict values
        new_values = loaded_model.predict(x=input_X,batch_size=75,verbose=0) ###predict output value
    
        ##take the prob. of presence (new_value.item((0,1))) and put into numpy array
        new_band_values=[]
        for i in new_values:
            new_value=i[1]
            new_band_values.append(new_value)
        new_band_values=np.array(new_band_values)
    
        df=pd.read_csv(path+'/data/GIS/world_prediction_row_col.csv')
        row=df["row"]
        row=row.values
        col=df["col"]
        col=col.values
        
        #################################
        # subset output into rasterband #
        #################################
        for i in range(0,len(row)):
            new_band[int(row[i]),int(col[i])]=new_band_values[i]
        
        new_band[index_minb1]=np.nan #exclude lakes, inland seas, coastline
        
        src=rasterio.open(path+'/data/GIS/stack/stacked_env_variables.tif')
        profile=src.profile
        profile.update(count=1)
    
        #write to file
        with rasterio.open(path+'/results/{}/{}_predicted_map.tif'.format(spec,spec), 'w', **profile) as dst:
            dst.write(new_band, 1) 
        
    
        ####################################
        # create additional colormap image #
        ####################################
        
        clipped = rasterio.open(path+'/results/{}/{}_predicted_map.tif'.format(spec,spec))
    
        array_data = clipped.read(1,masked=True)
        array_data[index_minb1]=np.nan
        
        #create figure
        my_dpi=96
        fig, ax = plt.subplots(figsize=(4320/my_dpi, 1800/my_dpi))
        im=ax.imshow(array_data,cmap=custom_cmap,interpolation="none",vmin=0,vmax=0.99)#,filternorm=1)
        divider=make_axes_locatable(ax)
        cax=divider.append_axes("right",size="2%",pad=0.1)
        fig.colorbar(im,cax=cax)
        spec=spec.replace("_"," ")
        plt.yticks(fontsize=40)
        ax.set_title('%s prediction map'%spec,fontsize=80)
        
        #save to file
        spec=spec.replace(" ","_")
        plt.savefig(path+'/results/{}/{}_predicted_map_color.png'.format(spec,spec),dpi=my_dpi)
