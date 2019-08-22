from shapely.geometry import Point, MultiPolygon, Polygon, box
from shapely.ops import unary_union, transform
from functools import partial
import earthpy.spatial as es
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
import pyproj
import pycrs
import gdal
import tqdm
import os

class data_prep_handler():
    
    def __init__(self,occurrence_handler,gis_handler,verbose):
        
        self.occurrence_handler = occurrence_handler        
        self.gis_handler = gis_handler        
        self.verbose = verbose    
        
        self.create_presence_maps()        
        self.gis_handler.reload_tifs()        
        #self.create_raster_stack()
        self.raster_stack_clip()
        self.create_presence_pseudo_absence()
        
    def create_presence_maps(self):
        
        src=rasterio.open(self.gis_handler.empty_map)
        profile=src.profile
        band=src.read(1)    
        if not os.path.isdir(self.gis_handler.presence):
            os.makedirs(self.gis_handler.presence,exist_ok=True)    
        for key in (tqdm.tqdm(self.occurrence_handler.species_dictionary(),desc='Creating presence maps' + (28 * ' ')) if self.verbose else self.occurrence_handler.species_dictionary()):
            new_band = band.copy()
            presence_data = self.occurrence_handler.species_dictionary()[key]
            presence_data['present/pseudo_absent']=1
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
                
    def create_raster_stack(self):
        
        if self.verbose:
            print('Creating raster stack' + (29 * ' ') + ':',end='')        
        if not os.path.isdir(self.gis_handler.stack):
            os.makedirs(self.gis_handler.stack,exist_ok=True)         
        es.stack(self.gis_handler.variables, self.gis_handler.stack + '/stacked_env_variables.tif')                
        if self.verbose:
            print(' Done!')
            
    def raster_stack_clip(self):
    
        def buff_on_globe(points, radius):
            
            geometry_list = [disk_on_globe(points.iloc[g], radius) for g in range(len(points))]
            polygon_list = []
            for geometry in geometry_list:
                if isinstance(geometry, MultiPolygon):
                    for polygon in geometry:
                        polygon_list += [polygon]
                elif isinstance(geometry, Polygon):
                    polygon_list += [geometry]
            return MultiPolygon(polygon_list)
        
        def disk_on_globe(point, radius):
        
            wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')
            lon, lat = point.dLon, point.dLat
            aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84', lat_0=lat, lon_0=lon)
            disk = transform(partial(pyproj.transform, aeqd, wgs84_globe), Point(0, 0).buffer(radius))        
            boundary = np.array(disk.boundary)
            i = 0
            while i < boundary.shape[0] - 1:
                if abs(boundary[i+1,0] - boundary[i,0]) > 180:
                    assert (boundary[i,1] > 0) == (boundary[i,1] > 0)
                    vsign = -1 if boundary[i,1] < 0 else 1
                    hsign = -1 if boundary[i,0] < 0 else 1
                    boundary = np.insert(boundary, i+1, [[hsign*180, boundary[i,1]], [hsign*180, vsign*90], [-hsign*180, vsign*90], [-hsign*180, boundary[i+1,1]]], axis=0)
                    i += 5
                else:
                    i += 1
            disk = Polygon(boundary)
            disk = disk.buffer(0)        
            if not disk.intersects(Point(lon, lat)):
                disk = box(-180, -90, 180, 90).difference(disk)        
            return disk
        
        if not os.path.isdir(self.gis_handler.stack_clip):
            os.makedirs(self.gis_handler.stack_clip,exist_ok=True)
        for key in (tqdm.tqdm(self.occurrence_handler.spec_dict,desc='Creating raster clips' + (29 *' ')) if self.verbose else self.occurrence_handler.spec_dict):              
            data=self.occurrence_handler.spec_dict[key]
            spec = key                       
            data['coordinates'] = list(zip(data["dLon"], data["dLat"]))
            data['coordinates'] = data["coordinates"].apply(Point)
            data["present/pseudo_absent"]=1
            geo_data=gpd.GeoDataFrame(data, geometry='coordinates',crs={'init' :'epsg:4326'})
            buffer=buff_on_globe(geo_data,1000000)
            union_buffer = gpd.GeoSeries(unary_union(buffer)).iloc[0]
            raster=rasterio.open(self.gis_handler.stack + '/stacked_env_variables.tif')
            out_tif = self.gis_handler.stack_clip + '/%s_raster_clip.tif' % spec
            out_img, out_transform = rasterio.mask.mask(dataset=raster, shapes=[union_buffer],crop=True)
            out_meta = raster.meta.copy()
            epsg_code = int(raster.crs.data['init'][5:])
            out_meta.update({"driver": "GTiff", "height": out_img.shape[1], "width": out_img.shape[2], "transform": out_transform, "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()})
            with rasterio.open(out_tif, "w", **out_meta) as dest:
                dest.write(out_img)
                
    def create_presence_pseudo_absence(self):
    
        stack_path= self.gis_handler.stack + '/stacked_env_variables.tif'
        r2=gdal.Open(stack_path)
        for key in (tqdm.tqdm(self.occurrence_handler.spec_dict,desc='Sampling pseudo absence' + (27 * ' ')) if self.verbose else self.occurrence_handler.spec_dict): 
            presence_data = self.occurrence_handler.spec_dict[key]
            presence_data["present/pseudo_absent"]=1
            spec = key
            long=presence_data["dLon"]
            lati=presence_data["dLat"]
            long=pd.Series.tolist(long)
            lati=pd.Series.tolist(lati)
            src=rasterio.open(stack_path)
            array=src.read_masks(1)
            for i in range(0,len(presence_data)):
                row,col=src.index(long[i],lati[i])
                array[row,col]=1
            (y_index_2, x_index_2) = np.nonzero(array > 1)
            r = r2
            (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = r.GetGeoTransform()        
            x_coords = x_index_2 * x_size + upper_left_x + (x_size / 2)
            y_coords = y_index_2 * y_size + upper_left_y + (y_size / 2)
            lon_lat_array=np.stack((x_coords,y_coords)).T
            random_sample_size=0
            len_p=int(len(presence_data))        
            if len_p > 2000:
                random_sample_size=len_p
            else: 
                random_sample_size=2000       
            outer_random_sample_lon_lats=lon_lat_array[np.random.choice(lon_lat_array.shape[0], random_sample_size, replace=False), :]            
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
            new_data=pd.DataFrame({"gbif_id": gbif,"taxon_name":taxon,"dLon": lon, "dLat":lat, "present/pseudo_absent": psa})
            data=pd.concat([presence_data,new_data],ignore_index=True,sort=True)
            data=data[['taxon_name','gbif_id','dLon','dLat','present/pseudo_absent']]
            data["taxon_name"]=spec
            data["row_n"]=np.arange(len(data))             
            long=data["dLon"]
            lati=data["dLat"]
            long=pd.Series.tolist(long)
            lati=pd.Series.tolist(lati)
            src=rasterio.open(stack_path)
            array=src.read_masks(1)
            if not os.path.isdir(self.gis_handler.spec_ppa):
                os.makedirs(self.gis_handler.spec_ppa,exist_ok=True)
            data=data.reset_index(drop=True)
            data.to_csv(self.gis_handler.spec_ppa + '/%s_ppa_dataframe.csv'%spec)
            
            