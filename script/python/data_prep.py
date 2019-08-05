from shapely.geometry import Point
import matplotlib.pyplot as plt
import rasterio.mask
import fiona
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.plot import plotting_extent
from natsort import natsorted
import earthpy.spatial as es
import gdal
from osgeo import osr,gdal_array
import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
import os

file_dir=r'/Users/winand.hulleman/Documents/trait-geo-diverse-angiosperms'


#BIOCLIM dataset
#Read in location paths and raster names
list_bioclim_files=[]
names_bioclim=[]

for root, dirs, files in os.walk(file_dir+"/data/GIS/wc5"):
    for file in files:
        if file.endswith('.tif') and "stacked" not in file:
            list_bioclim_files.append(file_dir+"/data/GIS/wc5/"+file)
            name=file.replace(".tif","")
            names_bioclim.append(name)
            names_bioclim=natsorted(names_bioclim,key=lambda y: y.lower())
print(names_bioclim)

#ENVIREM dataset
#Read in location paths and raster names
list_envirem_files=[]
names_envirem=[]

for root, dirs, files in os.walk(file_dir+"/data/GIS/5_deg"):
    for file in files:
        if file.endswith('.tif') and "stacked" not in file:
            list_envirem_files.append(file_dir+"/data/GIS/5_deg/"+file)
            name=file.replace(".tif","")
            names_envirem.append(name)
            names_envirem=natsorted(names_envirem,key=lambda y: y.lower())
print(names_envirem)

pred_data=pd.read_csv(file_dir+'/data/GIS/world_locations_to_predict.csv')

long=pred_data["decimal_longitude"]
lati=pred_data["decimal_latitude"]
long=pd.Series.tolist(long)
lati=pd.Series.tolist(lati)

src = rasterio.open(file_dir+'/data/GIS/5_deg/Aspect_5deg.tif')
band= src.read(1,masked=True)
rasterio.plot.show(band)

new_band = band.copy()

#set raster cell mask values of land area to 0 (to differentiate it from the sea)
for i in range(0,len(pred_data)):
    row,col=src.index(long[i],lati[i])
    new_band[row,col]=0

fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(new_band,cmap="gray")
ax.set_title("land map",
         fontsize=20)
plt.show()

profile = src.profile
print(profile)

with rasterio.open(file_dir+'/data/GIS/empty_land_map.tif', 'w', **profile) as dst:
        dst.write(new_band.astype(rasterio.float32), 1)

#Habitat fragmentation
shp_fn=file_dir+'/data/GIS/tnc/Habitat_Fragmentation/wwf_ecos_hab_frag.shp'
rst_fn =file_dir+'/data/GIS/5_deg/Aspect_5deg.tif'
out_fn =file_dir+'/data/GIS/tnc/ecoregion_attribute_rasters/habitat_fragmentation.tif'

df=gpd.read_file(file_dir+'/data/GIS/tnc/Habitat_Fragmentation/wwf_ecos_hab_frag.shp')

rst = rasterio.open(rst_fn)
meta = rst.meta.copy()


src=rasterio.open(rst_fn)

with rasterio.open(out_fn, 'w', **meta) as out:
    out_arr = src.read(1)

    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(df.geometry, df.fragmntndx))

    burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform,all_touched=True)
    out.write_band(1, burned)
    
#Human Accessibility
shp_fn=file_dir+'/data/GIS/tnc/Human_Accessibility/wwf_ecos_human_access.shp'
rst_fn =file_dir+'/data/GIS/5_deg/Aspect_5deg.tif'
out_fn =file_dir+'/data/GIS/tnc/ecoregion_attribute_rasters/human_accessibility.tif'

df=gpd.read_file(file_dir+'/data/GIS/tnc/Human_Accessibility/wwf_ecos_human_access.shp')

rst = rasterio.open(rst_fn)
meta = rst.meta.copy()


src=rasterio.open(rst_fn)

with rasterio.open(out_fn, 'w', **meta) as out:
    out_arr = src.read(1)

    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(df.geometry, df.humAcc_ndx))

    burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform,all_touched=True)
    out.write_band(1, burned)
    
#Human Appropriation
shp_fn=file_dir+'/data/GIS/tnc/Human_Appropriation/wwf_ecos_hum_approp.shp'
rst_fn =file_dir+'/data/GIS/5_deg/Aspect_5deg.tif'
out_fn =file_dir+'/data/GIS/tnc/ecoregion_attribute_rasters/human_appropriation.tif'

df=gpd.read_file(file_dir+'/data/GIS/tnc/Human_Appropriation/wwf_ecos_hum_approp.shp')

rst = rasterio.open(rst_fn)
meta = rst.meta.copy()


src=rasterio.open(rst_fn)

with rasterio.open(out_fn, 'w', **meta) as out:
    out_arr = src.read(1)

    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(df.geometry, df.HumAppIndx))

    burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform,all_touched=True)
    out.write_band(1, burned)
    
#Mammal species richness
shp_fn=file_dir+'/data/GIS/tnc/Mammal_species_richness/wwf_ecos_mammal_spcs.shp'
rst_fn =file_dir+'/data/GIS/5_deg/Aspect_5deg.tif'
out_fn =file_dir+'/data/GIS/tnc/ecoregion_attribute_rasters/mammal_spr.tif'

df=gpd.read_file(file_dir+'/data/GIS/tnc/Mammal_species_richness/wwf_ecos_mammal_spcs.shp')

rst = rasterio.open(rst_fn)
meta = rst.meta.copy()


src=rasterio.open(rst_fn)

with rasterio.open(out_fn, 'w', **meta) as out:
    out_arr = src.read(1)

    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(df.geometry, df.mamml_spcs))

    burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform,all_touched=True)
    out.write_band(1, burned)
    

#Plant species richness
shp_fn=file_dir+'/data/GIS/tnc/Plant_Species_Richness/wwf_ecos_plant_spcs.shp'
rst_fn =file_dir+'/data/GIS/5_deg/Aspect_5deg.tif'
out_fn =file_dir+'/data/GIS/tnc/ecoregion_attribute_rasters/plant_spr.tif'

df=gpd.read_file(file_dir+'/data/GIS/tnc/Plant_Species_Richness/wwf_ecos_plant_spcs.shp')
rst = rasterio.open(rst_fn)
meta = rst.meta.copy()


src=rasterio.open(rst_fn)

with rasterio.open(out_fn, 'w', **meta) as out:
    out_arr = src.read(1)

    # this is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(df.geometry, df.plant_spcs))

    burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform,all_touched=True)
    out.write_band(1, burned)
    
#Ecoregion attribute dataset
#Read in location paths and raster names
list_eco_attrib_files=[]
names_eco_attrib=[]

for root, dirs, files in os.walk(file_dir+"/data/GIS/tnc/ecoregion_attribute_rasters"):
    for file in files:
        if file.endswith('.tif') and "ecoregions" not in file and "stacked" not in file:
            list_eco_attrib_files.append(file_dir+"/data/GIS/tnc/ecoregion_attribute_rasters/"+file)
            name=file.replace(".tif","")
            names_eco_attrib.append(name)
print(names_eco_attrib)


shp_fn=file_dir+'/data/GIS/tnc/tnc_terr_ecoregions.shp'
rst_fn =file_dir+'/data/GIS/5_deg/Aspect_5deg.tif'
out_fn =file_dir+'/data/GIS/tnc/ecoregions.tif'
df=gpd.read_file(file_dir+'/data/GIS/tnc/tnc_terr_ecoregions.shp')

rst = rasterio.open(rst_fn)
meta = rst.meta.copy()

src=rasterio.open(rst_fn)

with rasterio.open(out_fn, 'w', **meta) as out:
    out_arr = src.read(1)

    # This is where we create a generator of geom, value pairs to use in rasterizing
    shapes = ((geom,value) for geom, value in zip(df.geometry, df.WWF_MHTNUM))

    burned = rasterio.features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform,all_touched=True)
    out.write_band(1, burned)
    
clipped = rasterio.open(out_fn)
array = clipped.read(1)
array_data = clipped.read(1,masked=True)
array_meta = clipped.profile

fig, ax = plt.subplots(figsize=(24, 10))
ax.imshow(array_data,cmap="YlGn_r",interpolation="none",vmin=0,vmax=100)
ax.set_title('ecoregions map',fontsize=40)
plt.show

###create array of unique ecoregion codes and names
eco_names=df.WWF_MHTNAM.unique()
eco_codes=df.WWF_MHTNUM.unique()

####open empty landmap as source to subset values on
src=rasterio.open(file_dir+'/data/GIS/empty_land_map.tif')
profile=src.profile
band=src.read(1)

####open rasterized ecoregion map as source to extract values from
ecor=rasterio.open(file_dir+'/data/GIS/tnc/ecoregions.tif')
array=ecor.read(1)

for item in range(0,len(eco_codes)):
    new_band=band.copy()
    ecoregion=eco_names[item]
    ecoregion=ecoregion.replace(" ","_")
    ecoregion=ecoregion.replace("/","_")
    eco_subset=np.where(array==eco_codes[item])
    rows=eco_subset[0]
    cols=eco_subset[1]
    for i in range(0,len(rows)):
        new_band[rows[i],cols[i]]=1
    
    rasterio.plot.show(new_band)
    
    with rasterio.open(file_dir+'/data/GIS/tnc/ecoregion_rasters/%s_map.tif'%ecoregion,"w",**profile) as dst:
        dst.write(new_band.astype(rasterio.float32),1)
        
#Ecoregion dataset
#Read in location paths and raster names
list_ecoregion_files=[]
names_ecoregion=[]

for root, dirs, files in os.walk(file_dir+'/data/GIS/tnc/ecoregion_rasters'):
    for file in files:
        if file.endswith('.tif') and "time" not in file and "stacked" not in file and "UNC" not in file:
            list_ecoregion_files.append(file_dir+'/data/GIS/tnc/ecoregion_rasters/'+file)
            name=file.replace(".tif","")
            names_ecoregion.append(name)
            
#access file with list of taxa names
taxa=pd.read_csv(file_dir+"/data/crops_cleaned/taxalist.txt",header=None)
taxa.columns=["taxon"]


species_occ_dict={}

for i in taxa["taxon"]:
    taxon_data = pd.read_csv(file_dir+"/data/crops_cleaned/%s.csv"%i)
    #add species dataframe to dict
    species_occ_dict["%s"%i] = taxon_data  
    #check whether all species have been included and inspect dictionary
if len(species_occ_dict.keys())==len(taxa["taxon"]):
    print("All species dataframes now in dictionary")
else:
    print("Error: not all species dataframe included")
    
src=rasterio.open(file_dir+'/data/GIS/empty_land_map.tif')
band=src.read(1)

for key in species_occ_dict:
    new_band = band.copy()
    
    #lon_lat presence points
    presence_data = species_occ_dict[key]
    presence_data["present/pseudo_absent"]=1
    spec = key
    long=presence_data["decimalLongitude"]
    lati=presence_data["decimalLatitude"]
    long=pd.Series.tolist(long)
    lati=pd.Series.tolist(lati)

    #set raster cell mask values of presence locations to 100
    for i in range(0,len(presence_data)):
        row,col=src.index(long[i],lati[i])
        new_band[row,col]=1
        
    rasterio.plot.show(new_band)

    with rasterio.open(file_dir+'/data/GIS/spec_presence/%s_presence_map.tif'%spec, 'w', **profile) as dst:
        dst.write(new_band.astype(rasterio.float32), 1)
        
#Species occurrence dataset
#Read in location paths and raster names
list_species_files=[]
names_species=[]

for root, dirs, files in os.walk(file_dir+"/data/GIS/spec_presence"):
    for file in files:
        if file.endswith('.tif') and "stacked" not in file:
            list_species_files.append(file_dir+"/data/GIS/spec_presence/"+file)
            name=file.replace(".tif","")
            names_species.append(name)
            
#Stack ENVIREM+BIOCLIM+HISTORIC+ECOREGION+SPECIES datasets
list_variables=[]
list_names=[]


for item in list_bioclim_files:
    list_variables.append(item)   
for item in list_envirem_files:
    list_variables.append(item)
for item in list_eco_attrib_files:
    list_variables.append(item)
for item in list_ecoregion_files:
    list_variables.append(item)
for item in list_species_files:
    list_variables.append(item)
    
     
es.stack(list_variables, file_dir+"/data/GIS/env_stacked/stacked_env_variables.tif")


for item in names_bioclim:
    list_names.append(item)   
for item in names_envirem:
    list_names.append(item)
for item in names_eco_attrib:
    list_names.append(item)
for item in names_ecoregion:
    list_names.append(item)
for item in names_species:
    list_names.append(item)
    
#save the names of the variables in order to list
myfile = open(file_dir+'/data/GIS/env_stacked/variable_list.txt', 'w+')
for item in list_names:
    myfile.write(item+"\n")
myfile.close()