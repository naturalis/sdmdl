from shapely.geometry import Point, MultiPolygon, Polygon, box
from shapely.ops import unary_union, transform
from functools import partial
import geopandas as gpd
import numpy as np
import rasterio
import pyproj
import pycrs
import tqdm
import os

class raster_stack_clip_helper():
    
    def __init__(self,oh,gh,ch,verbose):
        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose
        
    def disk_on_globe(self, point, radius):
    
        '''disk_on_globe function used for creating geodesic buffers, taking into account coordinate singularities.'''
        
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
    
    def buff_on_globe(self, points, radius):
            
        '''buff_on_globe function that utilizes a geoseries object and for each point creates a geodesic buffer. Subsequently aggregates these buffers into one final buffer object'''
        
        geometry_list = [self.disk_on_globe(points.iloc[g], radius) for g in range(len(points))]
        polygon_list = []
        for geometry in geometry_list:
            if isinstance(geometry, MultiPolygon):
                for polygon in geometry:
                    polygon_list += [polygon]
            elif isinstance(geometry, Polygon):
                polygon_list += [geometry]
        return MultiPolygon(polygon_list)
    
    def path_exists(self):
        if not os.path.isdir(self.gh.stack_clip):
            os.makedirs(self.gh.stack_clip,exist_ok=True)   
        
    def data_to_spatial(self):
        self.data['coordinates'] = list(zip(self.data["dLon"], self.data["dLat"]))
        self.data['coordinates'] = self.data["coordinates"].apply(Point)
        self.data["present/pseudo_absent"]=1
        
    def spatial_to_point(self):
        self.geo_data=gpd.GeoDataFrame(self.data, geometry='coordinates',crs={'init' :'epsg:4326'})
        
    def output(self):
        self.out_tif = self.gh.stack_clip + '/%s_raster_clip.tif' % self.key
        self.out_img, out_transform = rasterio.mask.mask(dataset=self.raster, shapes=[self.union_buffer],crop=True)
        self.out_meta = self.raster.meta.copy()
        epsg_code = int(self.raster.crs.data['init'][5:])
        self.out_meta.update({"driver": "GTiff", "height": self.out_img.shape[1], "width": self.out_img.shape[2], "transform": out_transform, "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()})
        
    def raster_stack_clip(self):
    
        self.path_exists()
        
        for self.key in (tqdm.tqdm(self.oh.spec_dict,desc='Creating raster clips' + (29 *' ')) if self.verbose else self.oh.spec_dict):  
            self.data=self.oh.spec_dict[self.key] 
            self.data_to_spatial()
            self.spatial_to_point()
            buffer=self.buff_on_globe(self.geo_data,1000000)  
            self.union_buffer = gpd.GeoSeries(unary_union(buffer)).iloc[0]
            self.raster=rasterio.open(self.gh.stack + '/stacked_env_variables.tif') 
            self.output()
        
        with rasterio.open(self.out_tif, "w", **self.out_meta) as dest:
            dest.write(self.out_img)