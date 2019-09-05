import pandas as pd
import numpy as np
import rasterio
import gdal
import tqdm
import os


# Why is this not called PresencePseudoAbsence?
# What does this class do? There should be documentation
class PresencePseudoAbsence:

    # This constructor should inherit from a superclass. It
    # does the same thing as all the other data_prep classes,
    # at least the first 4 lines.
    def __init__(self, oh, gh, ch, verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose
        self.random_sample_size = 2000
        self.random_seed = self.ch.random_seed

    def draw_random_absence(self, key):

        np.random.seed(self.random_seed)
        r = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        presence_data = self.oh.spec_dict[key]
        presence_data["present/pseudo_absent"] = 1
        spec = key
        long = presence_data["dLon"]
        lati = presence_data["dLat"]
        long = pd.Series.tolist(long)
        lati = pd.Series.tolist(lati)
        src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        array = src.read_masks(1)
        for i in range(0, len(presence_data)):
            row, col = src.index(long[i], lati[i])
            array[row, col] = 1
        (y_index_2, x_index_2) = np.nonzero(array > 1)
        (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = r.GetGeoTransform()
        x_coords = x_index_2 * x_size + upper_left_x + (x_size / 2)
        y_coords = y_index_2 * y_size + upper_left_y + (y_size / 2)
        lon_lat_array = np.stack((x_coords, y_coords)).T
        len_p = int(len(presence_data))
        if len_p > self.random_sample_size:
            sample_size = len_p
        else:
            sample_size = 2000
        outer_random_sample_lon_lats = lon_lat_array[
                                       np.random.choice(lon_lat_array.shape[0], sample_size, replace=False), :]
        return presence_data, outer_random_sample_lon_lats

    def create_presence_pseudo_absence(self):
        for key in (tqdm.tqdm(self.oh.spec_dict,
                              desc='Sampling pseudo absence' + (27 * ' ')) if self.verbose else self.oh.spec_dict):
            presence_data, outer_random_sample_lon_lats = self.draw_random_absence(key)
            lon = []
            lat = []
            psa = [0] * self.random_sample_size
            taxon = ["%s" % key] * self.random_sample_size
            gbif = ["no_id"] * self.random_sample_size
            for item in outer_random_sample_lon_lats:
                longitude = item[0]
                latitude = item[1]
                lon.append(longitude)
                lat.append(latitude)
            # these keys should not be hardcoded here
            new_data = pd.DataFrame(
                {"gbif_id": gbif, "taxon_name": taxon, "dLon": lon, "dLat": lat, "present/pseudo_absent": psa})
            data = pd.concat([presence_data, new_data], ignore_index=True, sort=True)

            # these keys should not be hardcoded here
            data = data[['taxon_name', 'gbif_id', 'dLon', 'dLat', 'present/pseudo_absent']]
            data["taxon_name"] = key
            data["row_n"] = np.arange(len(data))
            long = data["dLon"]
            lati = data["dLat"]
            long = pd.Series.tolist(long)
            lati = pd.Series.tolist(lati)
            src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
            array = src.read_masks(1)
            if not os.path.isdir(self.gh.spec_ppa):
                os.makedirs(self.gh.spec_ppa, exist_ok=True)
            data = data.reset_index(drop=True)
            data.to_csv(self.gh.spec_ppa + '/%s_ppa_dataframe.csv' % key)
