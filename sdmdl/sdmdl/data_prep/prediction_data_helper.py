import gdal
import numpy as np
import rasterio
import pandas as pd
import os

# Why is this not called PredictionData?
# Why is this not documented?
class PredictionDataHelper:

    # This has the same constructor as all the other
    # data_prep classes, it seems. They should all
    # inherit from the same superclass so that this
    # is only set once.
    def __init__(self, oh, gh, ch, verbose):
        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def prepare_prediction_df(self):
        array = gdal.Open(self.gh.stack + '/stacked_env_variables.tif').ReadAsArray()
        src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        df = pd.read_csv(self.gh.gis + '/world_locations_to_predict.csv')
        mean_std = pd.read_csv(self.gh.gis + '/env_bio_mean_std.txt', sep="\t")
        len_df = np.arange(len(df))
        
        # these should not be hardcoded here
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
        row = row.values
        col = col.values

        if not os.path.isdir(self.gh.gis):
            os.mkdir(self.gh.gis)

        np.save(self.gh.gis + '/world_prediction_array.npy', input_X)
        row_col.to_csv(self.gh.gis + '/world_prediction_row_col.csv')
