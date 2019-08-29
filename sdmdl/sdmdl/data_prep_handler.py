from shapely.geometry import Point, MultiPolygon, Polygon, box
from shapely.ops import unary_union, transform
from functools import partial
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
    """data_prep_handler object that manages all data preperation steps."""

    def __init__(self, occurrence_handler, gis_handler, config_handler, verbose):

        """data_prep_handler object initiation."""

        self.oh = occurrence_handler
        self.gh = gis_handler
        self.ch = config_handler
        self.verbose = verbose

    def create_presence_maps(self):

        """create_presence_maps function creates a set of presence maps from occurrence tables."""

        from sdmdl.sdmdl.data_prep.createpresencemaphelper import CreatePresenceMapHelper
        cpm = CreatePresenceMapHelper(self.oh, self.gh, self.ch, self.verbose)
        cpm.create_presence_maps()

    def create_raster_stack(self):

        """create_raster_stack function that combines all present .tif layers into one file."""

        from sdmdl.sdmdl.data_prep.create_raster_stack_helper import create_raster_stack_helper
        crs = create_raster_stack_helper(self.oh, self.gh, self.ch, self.verbose)
        crs.create_raster_stack()

    def raster_stack_clip(self):

        """raster_stack_clip function that creates a unique (clipped) raster file for further parameter extraction."""

        from sdmdl.sdmdl.data_prep.raster_stack_clip_helper import raster_stack_clip_helper
        rsc = raster_stack_clip_helper(self.oh, self.gh, self.ch, self.verbose)
        rsc.raster_stack_clip()

    def create_presence_pseudo_absence(self):

        """create_presence_pseudo_absence function that creates a random set of pseudo absences based on a specific
        buffer size. """

        np.random.seed(1)

        stack_path = self.gh.stack + '/stacked_env_variables.tif'
        r2 = gdal.Open(stack_path)
        for key in (tqdm.tqdm(self.oh.spec_dict,
                              desc='Sampling pseudo absence' + (27 * ' ')) if self.verbose else self.oh.spec_dict):
            presence_data = self.oh.spec_dict[key]
            presence_data["present/pseudo_absent"] = 1
            spec = key
            long = presence_data["dLon"]
            lati = presence_data["dLat"]
            long = pd.Series.tolist(long)
            lati = pd.Series.tolist(lati)
            src = rasterio.open(stack_path)
            array = src.read_masks(1)
            for i in range(0, len(presence_data)):
                row, col = src.index(long[i], lati[i])
                array[row, col] = 1
            (y_index_2, x_index_2) = np.nonzero(array > 1)
            r = r2
            (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = r.GetGeoTransform()
            x_coords = x_index_2 * x_size + upper_left_x + (x_size / 2)
            y_coords = y_index_2 * y_size + upper_left_y + (y_size / 2)
            lon_lat_array = np.stack((x_coords, y_coords)).T
            random_sample_size = 0
            len_p = int(len(presence_data))
            if len_p > 2000:
                random_sample_size = len_p
            else:
                random_sample_size = 2000
            outer_random_sample_lon_lats = lon_lat_array[
                                           np.random.choice(lon_lat_array.shape[0], random_sample_size, replace=False),
                                           :]  ##
            lon = []
            lat = []
            psa = [0] * (random_sample_size)
            taxon = ["%s" % spec] * (random_sample_size)
            gbif = ["no_id"] * (random_sample_size)
            for item in outer_random_sample_lon_lats:
                longitude = item[0]
                latitude = item[1]
                lon.append(longitude)
                lat.append(latitude)
            new_data = pd.DataFrame(
                {"gbif_id": gbif, "taxon_name": taxon, "dLon": lon, "dLat": lat, "present/pseudo_absent": psa})
            data = pd.concat([presence_data, new_data], ignore_index=True, sort=True)
            data = data[['taxon_name', 'gbif_id', 'dLon', 'dLat', 'present/pseudo_absent']]
            data["taxon_name"] = spec
            data["row_n"] = np.arange(len(data))
            long = data["dLon"]
            lati = data["dLat"]
            long = pd.Series.tolist(long)
            lati = pd.Series.tolist(lati)
            src = rasterio.open(stack_path)
            array = src.read_masks(1)
            if not os.path.isdir(self.gh.spec_ppa):
                os.makedirs(self.gh.spec_ppa, exist_ok=True)
            data = data.reset_index(drop=True)
            data.to_csv(self.gh.spec_ppa + '/%s_ppa_dataframe.csv' % spec)

    def calc_band_mean_and_stddev(self):

        """calc_band_mean_and_stddev function that calculates the mean and standard deviation of each band in the
        raster stack """

        raster = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        profile = raster.profile
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

    def create_training_df(self):

        """create_training_df function that creates the inputs for model training"""

        src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        inRas = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        for i in self.oh.name:
            data = pd.read_csv(self.gh.spec_ppa + '/%s_ppa_dataframe.csv' % i)
            spec = data["taxon_name"][0]
            spec = spec.replace(" ", "_")
            print("processing species ", spec)
            len_pd = np.arange(len(data))
            long = data["dLon"]
            lati = data["dLat"]
            ppa = data["present/pseudo_absent"]
            lon = long.values
            lat = lati.values
            row = []
            col = []
            for i in len_pd:
                row_n, col_n = src.index(lon[i], lat[i])  # spatial --> image coordinates
                row.append(row_n)
                col.append(col_n)
            myarray = inRas.ReadAsArray()
            mean_std = pd.read_csv(self.gh.gis + '/env_bio_mean_std.txt', sep="\t")
            mean_std = mean_std.to_numpy()
            X = []
            species = ["%s" % spec] * int(len(row))
            for j in range(0, self.gh.length):
                band = myarray[j]
                x = []
                for i in range(0, len(row)):
                    value = band[row[i], col[i]]
                    if j < self.gh.scaled_len:
                        if value < -1000:
                            value = np.nan
                        else:
                            value = ((value - mean_std.item((j, 1))) / mean_std.item((j, 2)))  # scale values
                        x.append(value)
                    if j >= self.gh.scaled_len:
                        if value < -1000:
                            value = np.nan
                        else:
                            value = value
                        x.append(value)
                X.append(x)
            X = np.array([np.array(xi) for xi in X])
            df = pd.DataFrame(X)
            df = df.T
            df["present/pseudo_absent"] = ppa
            df["dLat"] = lati
            df["dLon"] = long
            df["taxon_name"] = species
            df["present/pseudo_absent"] = ppa
            df["row_n"] = row
            df.rename(columns=dict(zip(df.columns[0:self.gh.length], self.gh.names)), inplace=True)
            df = df.dropna(axis=0, how='any')
            input_data = df
            if not os.path.isdir(self.gh.spec_ppa_env):
                os.makedirs(self.gh.spec_ppa_env, exist_ok=True)
            input_data.to_csv(self.gh.spec_ppa_env + '/%s_env_dataframe.csv' % spec)

    def create_prediction_df(self):

        """create_prediction_df function that creates a global prediction dataframe."""

        if self.verbose:
            print('Creating prediction dataframe' + (21 * ' ') + ':', end='')
        inRas = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        myarray = inRas.ReadAsArray()
        df = pd.read_csv(self.gh.gis + '/world_locations_to_predict.csv')
        len_pd = np.arange(len(df))
        lon = df["decimal_longitude"]
        lat = df["decimal_latitude"]
        lon = lon.values
        lat = lat.values
        row = []
        col = []
        src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        for i in len_pd:
            row_n, col_n = src.index(lon[i], lat[i])  # spatial --> image coordinates
            row.append(row_n)
            col.append(col_n)
        mean_std = pd.read_csv(self.gh.gis + '/env_bio_mean_std.txt', sep="\t")
        mean_std = mean_std.to_numpy()
        X = []
        for j in range(0, self.gh.length):
            band = myarray[j]
            x = []
            for i in range(0, len(row)):
                if j < self.gh.scaled_len:
                    value = band[row[i], col[i]]
                    value = ((value - mean_std.item((j, 1))) / mean_std.item((j, 2)))  # scale values
                    x.append(value)
                if j >= self.gh.scaled_len:
                    value = band[row[i], col[i]]
                    x.append(value)
            X.append(x)
        X.append(row)
        X.append(col)
        X = np.array([np.array(xi) for xi in X])
        df = pd.DataFrame(X)
        df = df.T
        df.rename(columns=dict(zip(df.columns[0:self.gh.length], self.gh.names)), inplace=True)
        df = df.dropna(axis=0, how='any')
        df.head()
        input_X = df.iloc[:, 0:self.gh.length]
        np.shape(input_X)
        row = df[self.gh.length]
        col = df[self.gh.length + 1]
        row_col = pd.DataFrame({"row": row, "col": col})
        input_X = input_X.values
        row = row.values
        col = col.values
        np.save(self.gh.gis + '/world_prediction_array.npy', input_X)
        row_col.to_csv(self.gh.gis + '/world_prediction_row_col.csv')
        if self.verbose:
            print(' Done!')
