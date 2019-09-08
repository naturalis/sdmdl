import gdal
import numpy as np
import rasterio
import pandas as pd
import os
import tqdm

class PredictionData:

    """Prepares (global) prediction dataset using a raster stack, a set of predefined points and a set of
    band means and standard deviations.

    :param gh: a GIS object: holds path and file names required for permutation of gis data.
    :param verbose: a boolean: prints a progress bar if True, silent if False

    :return: Object. Used to create a numpy (.npy) file containing the input data to the predictor. Performed
    by calling class method create_prediction_df on PredictionData object.
    """

    def __init__(self, gh, verbose):
        self.gh = gh
        self.verbose = verbose

    def prepare_prediction_df(self):

        """Loads raster stack, prediction locations and band statistics.

        :return: Tuple. containing:
        lists 'lon' and 'lat' contain the values of the longitude and latitude columns in
        'world_locations_to_predict.csv';
        lists 'row' and 'col' contain the values from the previous 'lon' and 'lat' columns converted from WGS84 to
        image coordinates;
        matrix 'array' is an multi-dimensional array representation of the raster stack;
        table 'mean_std' is an table containing the mean and standard deviation for each of the scaled raster layers
        """

        array = gdal.Open(self.gh.stack + '/stacked_env_variables.tif').ReadAsArray()
        src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        # world_locations_to_predict.csv is currently still included in the data folder (on the sdmdl github).
        # Due to this predictions can only be given globaly.
        df = pd.read_csv(self.gh.gis + '/world_locations_to_predict.csv')
        mean_std = pd.read_csv(self.gh.gis + '/env_bio_mean_std.txt', sep="\t")
        len_df = np.arange(len(df))
        
        # these are hard coded because for now these values come from the world_locations_to_predict.csv
        # which is included in the repository (for now).
        lon = df["decimal_longitude"].values
        lat = df["decimal_latitude"].values
        row = []
        col = []

        for i in len_df:
            row_n, col_n = src.index(lon[i], lat[i])
            row.append(row_n)
            col.append(col_n)
        mean_std = mean_std.to_numpy()

        return lon, lat, row, col, array, mean_std

    def create_prediction_df(self):

        """Creates (global) prediction dataset by extracting all environmental variables at each occurrence combination
        in the 'world_locations_to_predict.csv' file.

        :param self: a class instance of PredictionData

        :return: None. Does not return value or object, instead writes the computed prediction dataset to
        'world_prediction_array.npy' file
        """

        for _ in tqdm.tqdm([0], desc='Computing prediction data' + (25 * ' '), leave=True) if self.verbose else [0]:
            lon, lat, row, col, array, mean_std = self.prepare_prediction_df()
            X = []

            for j in range(0, self.gh.length):
                band = array[j]
                x = []

                for i in range(0, len(row)):
                    if j < self.gh.scaled_len:
                        value = band[row[i], col[i]]
                        value = ((value - mean_std.item((j, 1))) / mean_std.item((j, 2)))
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

            if not os.path.isdir(self.gh.gis):
                os.mkdir(self.gh.gis)

            np.save(self.gh.gis + '/world_prediction_array.npy', input_X)
            row_col.to_csv(self.gh.gis + '/world_prediction_row_col.csv')
