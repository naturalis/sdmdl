from sdmdl.sdmdl.import_variable_list import import_variable_list
import numpy as np
import rasterio
import tqdm

def calc_band_mean_and_stddev(path,verbose=True):
    
    _,_,var_len = import_variable_list(path)   
    
    raster=rasterio.open(path+'/data/GIS/stack/stacked_env_variables.tif')
    profile=raster.profile
    
    with open(path+'/data/GIS/env_bio_mean_std.txt','w+') as file:
        file.write("band"+"\t"+"mean"+"\t"+"std_dev"+"\n")
        file.close()
        
    for i in (tqdm.tqdm(range(1,var_len),desc='Computing band means and standard deviations' + (6 * ' ')) if verbose else range(1,var_len)):
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
        with open(path+'/data/GIS/env_bio_mean_std.txt','a') as file:
            file.write(str(i)+"\t"+str(mean)+"\t"+str(std_dev)+"\n")