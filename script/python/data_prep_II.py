from shapely.geometry import Point
import matplotlib.pyplot as plt
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.plot import plotting_extent
import gdal
import pandas as pd
import numpy as np
import geopandas
import rasterio
import pycrs

file_dir=r'/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms'

var_names = open(file_dir+"/data/gis/env_stacked/variable_list.txt")
var_names = var_names.read()
var_names = var_names.split("\n")[1:-1]

#access file with list of taxa names
taxa=pd.read_csv(file_dir+"/data/crops_cleaned/taxalist.txt",header=None)
taxa.columns=["taxon"]

species_occ_dict={}

for i in taxa["taxon"]:
    taxon_data = pd.read_csv(file_dir+"/data/crops_cleaned/%s.csv"%i)
    species_occ_dict["%s"%i] = taxon_data  
    #check whether all species have been included and inspect dictionary
if len(species_occ_dict.keys())==len(taxa["taxon"]):
    print("All species dataframes now in dictionary")
else:
    print("Error: not all species dataframe included")
    
for key in species_occ_dict:  
    #load occurrence data and set initial projection
    data=species_occ_dict[key]
    spec = key

    data['coordinates'] = list(zip(data["decimalLongitude"], data["decimalLatitude"]))
    data['coordinates'] = data["coordinates"].apply(Point)
    data["present/pseudo_absent"]=1
    geo_data=geopandas.GeoDataFrame(data, geometry='coordinates',crs={'init' :'epsg:4326'})

    #change projection to azimuthal equidistant to calculate 1000km buffer around point
    geo_data = geo_data.to_crs({'init': 'esri:54032'}) 
    buffer=geo_data.buffer(1000*1000)
    buffer=buffer.to_crs(epsg=4326)

    #create single large polygon from individual buffers
    union_buffer=buffer.unary_union

    #first clip the raster based on this extend 
    raster=rasterio.open(file_dir+'/data/gis/env_stacked/stacked_env_variables.tif')
    
    #specify output tif:
    out_tif = file_dir+'/data/GIS/spec_stacked_raster_clip/%s_raster_clip.tif'%spec

    #clip the raster:
    out_img, out_transform = rasterio.mask.mask(dataset=raster, shapes=[union_buffer],crop=False)

    # Copy the metadata
    out_meta = raster.meta.copy()

    # Parse EPSG code
    epsg_code = int(raster.crs.data['init'][5:])
    out_meta.update({"driver": "GTiff",
                     "height": out_img.shape[1],
                     "width": out_img.shape[2],
                     "transform": out_transform,
                     "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()})

    with rasterio.open(out_tif, "w", **out_meta) as dest:
            dest.write(out_img)
            
#Inspect the first band of the clipped raster for all species
for key in species_occ_dict:
    
    # Extract occurrence point to plot on the raster (see if correct area was clipped)
    data=species_occ_dict[key]
    spec = key
    data['coordinates'] = list(zip(data["decimalLongitude"], data["decimalLatitude"]))
    data['coordinates'] = data["coordinates"].apply(Point)
    geo_data=geopandas.GeoDataFrame(data, geometry='coordinates',crs={'init' :'epsg:4326'})
    
    # open the clipped raster
    clipped = rasterio.open(file_dir+'/data/GIS/spec_stacked_raster_clip/%s_raster_clip.tif'%spec)
    array = clipped.read(1)
    array_data = clipped.read(1,masked=True)
    array_meta = clipped.profile
   
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(array_data,cmap="gist_earth",interpolation="none",vmin=0,
    
    # Plot the occurrence points on the raster
    extent=plotting_extent(clipped),)
    spec_plots_points=geo_data["coordinates"]
    spec_plots_points.plot(ax=ax,
                       marker='o',
                       markersize=20,
                       color='red')
    ax.set_title("%s \n Raster clip and occurrence points"%spec,
             fontsize=20)
    plt.show()
    
#Works!
    
#open world raster
stack_path=file_dir+'/data/GIS/env_stacked/stacked_env_variables.tif'
r2=gdal.Open(stack_path)


for key in species_occ_dict: 
    
    #extract longitude and latitude of occurrence locations and label them as present (1)
    presence_data = species_occ_dict[key]
    presence_data["present/pseudo_absent"]=1
    spec = key
    
    long=presence_data["decimalLongitude"]
    lati=presence_data["decimalLatitude"]
    long=pd.Series.tolist(long)
    lati=pd.Series.tolist(lati)
   
    #read raster
    src=rasterio.open(stack_path)
    array=src.read_masks(1)
    
    # set raster cell mask values of presence locations to threshold value (=1) to exclude them from pseudo-absence sampling
    for i in range(0,len(presence_data)):
        row,col=src.index(long[i],lati[i])
        array[row,col]=1
    
    #subset of cells with datavalues from which to sample pseudo-absences
    (y_index_2, x_index_2) = np.nonzero(array > 1) 
    
    #sample random locations from raster excluding sea and presence cells
    r=r2
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = r.GetGeoTransform()
    
    x_coords = x_index_2 * x_size + upper_left_x + (x_size / 2) #add half the cell size
    y_coords = y_index_2 * y_size + upper_left_y + (y_size / 2) #to centre the point

    lon_lat_array=np.stack((x_coords,y_coords)).T

    #determine number of pseudo-absences to sample
    random_sample_size=0
    len_p=int(len(presence_data))
    
    if len_p > 2000:
        random_sample_size=len_p
    else: 
        random_sample_size=2000
   
    outer_random_sample_lon_lats=lon_lat_array[np.random.choice(lon_lat_array.shape[0], random_sample_size, replace=False), :] ##
    print(len(outer_random_sample_lon_lats), "number of outer pseudo absences")
    
     
    #Add selected cells to dataset
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
    data=pd.concat([presence_data,new_data],ignore_index=True)
    data=data[['taxon_name','gbif_id','decimalLongitude','decimalLatitude','present/pseudo_absent']]
    data["taxon_name"]=spec
    data["row_n"]=np.arange(len(data))
     
    long=data["decimalLongitude"]
    lati=data["decimalLatitude"]
    long=pd.Series.tolist(long)
    lati=pd.Series.tolist(lati)
    
    print(len(data),"lenght data with pseudo absences pre-filtering")
    
    #read raster
    src=rasterio.open(stack_path)
    array=src.read_masks(1)
        
    data=data.reset_index(drop=True)
    data.to_csv(file_dir + "/data/spec_ppa/%s_ppa_dataframe.csv"%spec)

#next species
    
raster=rasterio.open(file_dir+'/data/GIS/env_stacked/stacked_env_variables.tif')
array = raster.read()
profile=raster.profile

with open(file_dir+'/data/GIS/env_bio_mean_std.txt','w+') as file:
    file.write("band"+"\t"+"mean"+"\t"+"std_dev"+"\n")
    file.close()
    
for i in range(1,65):
    print(i)
    profile.update(count=1)
    band=raster.read(i)
    band[band < -9999] = -9999
    where_are_NaNs = np.isnan(band)
    band[where_are_NaNs] = -9999
    band_masked = np.ma.masked_array(band, mask=(band == -9999))

    #calculate mean and std.dev of each band
    mean=band_masked.mean()
    std_dev=np.std(band_masked)

    #write to file
    with open(file_dir+'/data/GIS/env_bio_mean_std.txt','a') as file:
        file.write(str(i)+"\t"+str(mean)+"\t"+str(std_dev)+"\n")
        

#access file with list of taxa names
taxa=pd.read_csv(file_dir+"/data/crops_cleaned/taxalist.txt",header=None)
taxa.columns=["taxon"]

src=rasterio.open(file_dir+'/data/GIS/env_stacked/stacked_env_variables.tif')
inRas=gdal.Open(file_dir+'/data/GIS/env_stacked/stacked_env_variables.tif')

for i in taxa["taxon"][:]:
    
    data = pd.read_csv(file_dir+"/data/spec_ppa/%s_ppa_dataframe.csv"%i)
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
    mean_std=pd.read_csv(file_dir+'/data/GIS/env_bio_mean_std.txt',sep="\t")
    mean_std=mean_std.to_numpy()


    ########################################################
    #extract the values for all bands and prepare input data
    ########################################################
    X=[]
    species =["%s"%spec]*int(len(row))

    for j in range(0,64):
        band=myarray[j]
        x=[]

      #extract coastal outline  
        
        for i in range(0,len(row)):
            value= band[row[i],col[i]]
            if j < 46:
                if value <-1000:
                    value=np.nan
                else:  
                    value = ((value - mean_std.item((j,1))) / mean_std.item((j,2)))#scale values
                x.append(value)
                
            if j >= 46:
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
    df.rename(columns=dict(zip(df.columns[0:186], var_names)),inplace=True)
    
    #drop any potential rows with no-data values
    df=df.dropna(axis=0, how='any')
    input_data=df
    
    ##save input dataframe
    input_data.to_csv(file_dir +"/data/spec_ppa_env/%s_env_dataframe.csv"%spec)
    
##opening raster as 3d numpy array
inRas=gdal.Open(file_dir+'/data/GIS/env_stacked/stacked_env_variables.tif')
myarray=inRas.ReadAsArray()
print(myarray.shape)
print(type(myarray))

#get all collumn and row values for all cells to predict over 
df=pd.read_csv(file_dir+'/data/GIS/world_locations_to_predict.csv')

len_pd=np.arange(len(df))
lon=df["decimal_longitude"]
lat=df["decimal_latitude"]
lon=lon.values
lat=lat.values

row=[]
col=[]

src=rasterio.open(file_dir+'/data/GIS/env_stacked/stacked_env_variables.tif')

for i in len_pd:
    row_n, col_n = src.index(lon[i], lat[i])# spatial --> image coordinates
    row.append(row_n)
    col.append(col_n)

#collect file with mean and std_dev for each band
mean_std=pd.read_csv(file_dir+'/data/GIS/env_bio_mean_std.txt',sep="\t")
mean_std=mean_std.to_numpy()


###########################################################
# extract the values for all bands and prepare input data #
###########################################################
X=[]

for j in range(0,65):
    print(j)
    band=myarray[j]
    x=[]

    for i in range(0,len(row)):
        if j < 46:
            value= band[row[i],col[i]]
            value = ((value - mean_std.item((j,1))) / mean_std.item((j,2)))#scale values
            x.append(value)
        if j >= 46:
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
    df.rename(columns=dict(zip(df.columns[0:65], var_names)),inplace=True)
    df=df.dropna(axis=0, how='any')
    df.head()
    
    input_X=df.iloc[:,0:65]
    np.shape(input_X)
    
    row=df[64]
    col=df[65]
    
    row_col=pd.DataFrame({"row":row,"col":col})
    
    #convert dataframe back to numpy array
    input_X=input_X.values
    
    #convert rows and col indices back to array
    row=row.values
    col=col.values
    
    #save
    prediction_array=np.save(file_dir+'/data/GIS/world_prediction_array.npy',input_X)
    prediction_pandas=row_col.to_csv(file_dir+'/data/GIS/world_prediction_row_col.csv')