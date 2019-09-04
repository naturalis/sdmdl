import numpy as np
import rasterio
import tqdm
import os

# Why is this not called BandStatisticsHelper?
class BandStatistics:

    # Why does this constructor look the same as that 
    # of the CreatePresenceMapHelper? That's what inheritance is for.
    def __init__(self, gh, verbose):
        self.gh = gh
        self.verbose = verbose

    def calc_band_mean_and_stddev(self):
        raster = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        profile = raster.profile

        if not os.path.isdir(self.gh.gis):
            os.mkdir(self.gh.gis)

        with open(self.gh.gis + '/env_bio_mean_std.txt', 'w+') as file:
            file.write("band" + "\t" + "mean" + "\t" + "std_dev" + "\n")
            file.close()

        tqdm_txt = 'Computing band means and standard deviations' + (6 * ' ')
        sl = self.gh.scaled_len + 1

        for i in (tqdm.tqdm(range(1, sl), desc=tqdm_txt) if self.verbose else range(1, sl)):
            profile.update(count=1)
            band = raster.read(i)
            band[band < -9999] = -9999
            na = np.isnan(band)
            band[na] = -9999
            band_masked = np.ma.masked_array(band, mask=(band == -9999))
            mean = band_masked.mean()
            std_dev = np.std(band_masked)
            with open(self.gh.gis + '/env_bio_mean_std.txt', 'a') as file:
                file.write(str(i) + "\t" + str(mean) + "\t" + str(std_dev) + "\n")
