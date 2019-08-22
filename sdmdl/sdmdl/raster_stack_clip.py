from shapely.geometry import Point, MultiPolygon, Polygon, box
from sdmdl.sdmdl.load_taxa_list import load_taxa_list
from shapely.ops import unary_union, transform
from functools import partial
import geopandas as gpd
import numpy as np
import rasterio
import pyproj
import pycrs
import tqdm
import os

def raster_stack_clip(path,verbose=True):
    
     # buff_on_globe function that draws geodesic buffers for a given GeoSeries object and radius.
    
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
    
    # disk_on_globe function that draws a geodesic buffer for a single datapoint. 
    # Also contains error correction code to prevent the creation of invalid geometries due to coordinate singularities in wgs84.
    
    def disk_on_globe(point, radius):
    
        wgs84_globe = pyproj.Proj(proj='latlong', ellps='WGS84')
        lon, lat = point.decimalLongitude, point.decimalLatitude
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
    
        assert disk.is_valid
        assert disk.boundary.is_simple
        assert disk.intersects(Point(lon, lat))
        return disk
    
    _,species_occ_dict = load_taxa_list(path)
    
    # Confirm that the stack_clip folder exists before writing files to it.
    
    if not os.path.isdir(path+'/data/GIS/stack_clip'):
        os.makedirs(path+'/data/GIS/stack_clip',exist_ok=True)
        
    # For each species in species dictionary.
    
    for key in (tqdm.tqdm(species_occ_dict,desc='Creating raster clips' + (29 *' ')) if verbose else species_occ_dict):  
        
        # Load occurrence data for 'key' species.
        
        data=species_occ_dict[key]
        spec = key
        
        # Checks wether the file is already present (TESTING FUNCTIONALITY!!!).
        
        if os.path.isfile(path+'/data/GIS/stack_clip/%s_raster_clip.tif'%spec):
            #print("\nskip %s..." % spec)
            continue
    
        # Create a set of point objects, one for each occurrence.
        
        data['coordinates'] = list(zip(data["decimalLongitude"], data["decimalLatitude"]))
        data['coordinates'] = data["coordinates"].apply(Point)
        data["present/pseudo_absent"]=1
        geo_data=gpd.GeoDataFrame(data, geometry='coordinates',crs={'init' :'epsg:4326'})
    
        # Create geodesic buffer with a radius of 1000000 (meters), and merge all buffers into one geometry.
        
        buffer=buff_on_globe(geo_data,1000000)
        union_buffer = gpd.GeoSeries(unary_union(buffer)).iloc[0]
    
        # Load raster stack.
        
        raster=rasterio.open(path+'/data/gis/stack/stacked_env_variables.tif')
        
        # Output path.
        
        out_tif = path + '/data/GIS/stack_clip/%s_raster_clip.tif' % spec
    
        # Clip the raster to reduce the size and computation requirements.
        
        out_img, out_transform = rasterio.mask.mask(dataset=raster, shapes=[union_buffer],crop=True)
    
        # Copy the metadata
        
        out_meta = raster.meta.copy()
    
        # Parse EPSG code
        
        epsg_code = int(raster.crs.data['init'][5:])
        out_meta.update({"driver": "GTiff", "height": out_img.shape[1], "width": out_img.shape[2], "transform": out_transform, "crs": pycrs.parse.from_epsg_code(epsg_code).to_proj4()})
    
        # Save stacked raster clip.
    
        with rasterio.open(out_tif, "w", **out_meta) as dest:
            dest.write(out_img)