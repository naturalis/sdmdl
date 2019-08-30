import pandas as pd
import numpy as np
import rasterio
import gdal
import tqdm
import os



class create_presence_pseudo_absence_helper:

    def __init__(self,oh,gh,ch,verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

        np.random.seed(1)
        self.random_sample_size = 0
        self.spec = ''
        self.outer_random_sample_lon_lats = []

        self.stack_path = self.gh.stack + '/stacked_env_variables.tif'

        self.r = gdal.Open(self.stack_path)

    def draw_random_absence(self):

        self.presence_data = self.oh.spec_dict[self.key]
        self.presence_data["present/pseudo_absent"] = 1
        self.spec = self.key
        long = self.presence_data["dLon"]
        lati = self.presence_data["dLat"]
        long = pd.Series.tolist(long)
        lati = pd.Series.tolist(lati)
        src = rasterio.open(self.stack_path)
        array = src.read_masks(1)
        for i in range(0, len(self.presence_data)):
            row, col = src.index(long[i], lati[i])
            array[row, col] = 1
        (y_index_2, x_index_2) = np.nonzero(array > 1)
        (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = self.r.GetGeoTransform()
        x_coords = x_index_2 * x_size + upper_left_x + (x_size / 2)
        y_coords = y_index_2 * y_size + upper_left_y + (y_size / 2)
        lon_lat_array = np.stack((x_coords, y_coords)).T
        len_p = int(len(self.presence_data))
        if len_p > 2000:
            self.random_sample_size = len_p
        else:
            self.random_sample_size = 2000
        self.outer_random_sample_lon_lats = lon_lat_array[
                                       np.random.choice(lon_lat_array.shape[0], self.random_sample_size, replace=False),:]
        return(self.presence_data)

    def create_ppa_df(self,presence_data):

        self.presence_data = presence_data
        lon = []
        lat = []
        psa = [0] * (self.random_sample_size)
        taxon = ["%s" % self.spec] * (self.random_sample_size)
        gbif = ["no_id"] * (self.random_sample_size)
        for item in self.outer_random_sample_lon_lats:
            longitude = item[0]
            latitude = item[1]
            lon.append(longitude)
            lat.append(latitude)
        new_data = pd.DataFrame(
            {"gbif_id": gbif, "taxon_name": taxon, "dLon": lon, "dLat": lat, "present/pseudo_absent": psa})
        data = pd.concat([self.presence_data, new_data], ignore_index=True, sort=True)
        data = data[['taxon_name', 'gbif_id', 'dLon', 'dLat', 'present/pseudo_absent']]
        data["taxon_name"] = self.spec
        data["row_n"] = np.arange(len(data))
        long = data["dLon"]
        lati = data["dLat"]
        long = pd.Series.tolist(long)
        lati = pd.Series.tolist(lati)
        src = rasterio.open(self.stack_path)
        array = src.read_masks(1)
        if not os.path.isdir(self.gh.spec_ppa):
            os.makedirs(self.gh.spec_ppa, exist_ok=True)
        data = data.reset_index(drop=True)
        data.to_csv(self.gh.spec_ppa + '/%s_ppa_dataframe.csv' % self.spec)

    def create_presence_pseudo_absence(self):
        for self.key in (tqdm.tqdm(self.oh.spec_dict, desc='Sampling pseudo absence' + (27 * ' ')) if self.verbose else self.oh.spec_dict):
            presence_data = self.draw_random_absence()
            self.create_ppa_df(presence_data)
