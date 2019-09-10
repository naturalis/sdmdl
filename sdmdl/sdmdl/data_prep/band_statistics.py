import numpy as np
import rasterio
import tqdm
import os


class BandStatistics:

    """Calculates the mean and standard deviation of all scaled environmental raster layers in a raster stack (.tif)
    file.

    :param gh: a GIS object: holds path and file names required for computation of gis data.
    :param verbose: a boolean: prints a progress bar if True, silent if False

    :return: Object. Used to create a text (.txt) file containing the mean and standard deviation for each layer in a
    raster stack. Performed by calling class method calc_band_mean_and_stddev on BandStatistics object.
    """

    def __init__(self, gh, verbose):
        self.gh = gh
        self.verbose = verbose

    def calc_band_mean_and_stddev(self):

        """Opens a raster stack and computes the mean and standard deviation for each scaled environmental layer in the
         stack.

        :return: None. Does not return value or object, instead writes the band mean and standard deviation of each band
        to a text (.txt) file.
        """

        raster = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        profile = raster.profile

        if not os.path.isdir(self.gh.gis):
            os.mkdir(self.gh.gis)

        with open(self.gh.gis + '/env_bio_mean_std.txt', 'w+') as file:
            file.write("band" + "\t" + "mean" + "\t" + "std_dev" + "\n")
            file.close()

        tqdm_txt = 'Computing band means and standard deviations' + (6 * ' ')
        sl = self.gh.scaled_len + 1

        for i in (tqdm.tqdm(range(1, sl), desc=tqdm_txt, leave=True) if self.verbose else range(1, sl)):
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
