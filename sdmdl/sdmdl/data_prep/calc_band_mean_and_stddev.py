import numpy as np
import rasterio
import tqdm
import os

class CalcBandMeanAndStddev:

    def __init__(self,oh,gh,ch,verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def calc_band_mean_and_stddev(self):
        raster = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        profile = raster.profile

        if not os.path.isdir(self.gh.gis):
            os.mkdir(self.gh.gis)

        with open(self.gh.gis + '/env_bio_mean_std.txt', 'w+') as file:
            file.write("band" + "\t" + "mean" + "\t" + "std_dev" + "\n")
            file.close()

        for i in (tqdm.tqdm(range(1, self.gh.scaled_len + 1),
                            desc='Computing band means and standard deviations' + (6 * ' ')) if self.verbose else range(
            1, self.gh.scaled_len + 1)):
            profile.update(count=1)
            band = raster.read(i)
            band[band < -9999] = -9999
            where_are_NaNs = np.isnan(band)
            band[where_are_NaNs] = -9999
            band_masked = np.ma.masked_array(band, mask=(band == -9999))
            mean = band_masked.mean()
            std_dev = np.std(band_masked)
            with open(self.gh.gis + '/env_bio_mean_std.txt', 'a') as file:
                file.write(str(i) + "\t" + str(mean) + "\t" + str(std_dev) + "\n")