import pandas as pd
import numpy as np
import rasterio
import gdal
import tqdm
import os


class PresencePseudoAbsence:

    """Samples a random selection of 'latitude' and 'longitude' coordinates that are included in the training dataset as
    absence locations. For each species in the Occurrence object (oh) creates a random sample (size of the sample can
    be set from the config.yml)

    :param oh: an Occurrence object: holds occurrence files and tables
    :param gh: a GIS object: holds path and file names required for computation of gis data.
    :param ch: a Config object: holds instance variables that determine the size of the random sample or random seed.
    :param verbose: a boolean: prints a progress bar if True, silent if False

    :return: Object. Used to randomly sample absence locations that are subsequently written to (.csv) file.
    Performed by calling class method create_presence_pseudo_absence on PresencePseudoAbsence object.
    """

    def __init__(self, oh, gh, ch, verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose
        self.random_sample_size = self.ch.pseudo_freq
        self.random_seed = self.ch.random_seed

    def draw_random_absence(self, key):

        """Draw a random sample of absences from terrestrial locations where no occurrences have been observed.

        :param self: a class instance of PresencePseudoAbsence
        :param key: string dictionary key (species name, e.g. Zea_mays_l) used to obtain the occurrences table.
        :return: Tuple. Containing:
        table 'presence_data' is a copy of the occurrence table held by the Occurrence object (oh) for
        species = key;
        matrix 'outer_random_sample_lon_lats' containing a random sample of absence locations;
        int 'sample_size' indicating the size of the drawn sample.
        """

        np.random.seed(self.random_seed)
        r = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        presence_data = self.oh.spec_dict[key]
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
        return presence_data, outer_random_sample_lon_lats, sample_size

    def create_presence_pseudo_absence(self):

        """Selects a random sample of absence locations for each species in the Occurrence object (oh).

        :param self: a class instance of PresencePseudoAbsence

        :return: None. Does not return value or object, instead combines the presence and absence datasets and writes
        the output to file for each species.
        """

        for key in (tqdm.tqdm(self.oh.spec_dict, desc='Sampling pseudo absence' + (27 * ' '), leave=True) if self.verbose else self.oh.spec_dict):
            presence_data, outer_random_sample_lon_lats, sample_size = self.draw_random_absence(key)
            presence_data['present/pseudo_absent'] = 1
            lon = []
            lat = []
            psa = [0] * sample_size
            for item in outer_random_sample_lon_lats:
                longitude = item[0]
                latitude = item[1]
                lon.append(longitude)
                lat.append(latitude)

            # these are hard coded because the table is written to file and are not involved in user input
            # occurrences or raster layers
            new_data = pd.DataFrame(
                {"dLon": lon, "dLat": lat, "present/pseudo_absent": psa})
            data = pd.concat([presence_data, new_data], ignore_index=True, sort=True)

            # once again these are columns of a data frame that is written to file.
            data = data[['dLon', 'dLat', 'present/pseudo_absent']]
            data["row_n"] = np.arange(len(data))
            if not os.path.isdir(self.gh.spec_ppa):
                os.makedirs(self.gh.spec_ppa, exist_ok=True)
            data = data.reset_index(drop=True)
            data.to_csv(self.gh.spec_ppa + '/%s_ppa_dataframe.csv' % key)
