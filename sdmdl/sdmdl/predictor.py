from mpl_toolkits.axes_grid1 import make_axes_locatable
from keras.models import model_from_json
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import numpy as np
import rasterio
import tqdm
import gdal

# I want to be called Predictor and I need proper
# class-level documentation
class Predictor:
    """predict_handler object that manages model predictions"""

    # Now I finally know what oh, gh, and ch are. 
    # 1. I have seen this same constructor now 9 times. This needs to be
    #    be moved to a single base class
    # 2. It is probably bad design that everyone holds a reference to 
    #    everyone else (Law of Demeter)
    def __init__(self, occurrence_handler, gis_handler, config_handler, verbose):

        """predict_handler object initiation"""

        self.oh = occurrence_handler
        self.gh = gis_handler
        self.ch = config_handler
        self.verbose = verbose

    def prep_color_scheme(self):
        norm = matplotlib.colors.Normalize(0, 1)
        # Put me in a config file
        colors = [[norm(0), "0.95"], [norm(0.05), "steelblue"], [norm(0.1), "sienna"], [norm(0.3), "wheat"],
                  [norm(0.5), "cornsilk"], [norm(0.95), "yellowgreen"], [norm(1.0), "green"]]
        custom_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
        custom_cmap.set_bad(color="white")
        fig, ax = plt.subplots()
        x = np.arange(10)
        y = np.linspace(-1, 1, 10)
        sc = ax.scatter(x, y, c=y, norm=norm, cmap=custom_cmap)
        fig.colorbar(sc, orientation="horizontal")
        return custom_cmap

    def prep_prediction_data(self):
        inRas = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        myarray = inRas.ReadAsArray()
        src = rasterio.open(self.gh.empty_map)
        b = src.read(1)
        minb = np.min(b)
        index_minb1 = np.where(b == minb)
        return myarray, index_minb1

    def predict_distribution(self,species,myarray,index_minb1):
        spec = species
        spec_index = self.gh.names.index("%s_presence_map" % spec)
        input_X = np.load(self.gh.gis + '/world_prediction_array.npy')  # %spec)
        np.shape(input_X)
        input_X = np.delete(input_X, [spec_index], 1)
        np.shape(input_X)
        new_band = myarray[1].copy()
        new_band.shape
        json_file = open(self.ch.result_path + '/{}/{}_model.json'.format(spec, spec), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights(self.ch.result_path + '/{}/{}_model.h5'.format(spec, spec))
        loaded_model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=0.001), metrics=['accuracy'])
        new_values = loaded_model.predict(x=input_X, batch_size=75, verbose=0)
        new_band_values = []
        for i in new_values:
            new_value = i[1]
            new_band_values.append(new_value)
        new_band_values = np.array(new_band_values)
        df = pd.read_csv(self.gh.gis + '/world_prediction_row_col.csv')

        # No hardcoded dictionary keys
        row = df["row"]
        row = row.values
        col = df["col"]
        col = col.values
        for i in range(0, len(row)):
            new_band[int(row[i]), int(col[i])] = new_band_values[i]
        new_band[index_minb1] = np.nan
        return new_band

    def predict_model(self):

        """performs global predictions and saves the resulting images (.png & .tif) to file"""
        custom_cmap = self.prep_color_scheme()
        myarray, index_minb1 = self.prep_prediction_data()
        for species in tqdm.tqdm(self.oh.name,
                                 desc='Predicting globally' + (31 * ' ')) if self.verbose else self.oh.name:
            spec = species
            new_band = self.predict_distribution(species, myarray, index_minb1)
            src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
            profile = src.profile
            profile.update(count=1)
            with rasterio.open(self.ch.result_path + '/{}/{}_predicted_map.tif'.format(spec, spec), 'w',
                               **profile) as dst:
                dst.write(new_band, 1)
            clipped = rasterio.open(self.ch.result_path + '/{}/{}_predicted_map.tif'.format(spec, spec))
            array_data = clipped.read(1, masked=True)
            array_data[index_minb1] = np.nan
            my_dpi = 96
            fig, ax = plt.subplots(figsize=(4320 / my_dpi, 1800 / my_dpi))
            im = ax.imshow(array_data, cmap=custom_cmap, interpolation="none", vmin=0, vmax=0.99)  # ,filternorm=1)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="2%", pad=0.1)
            fig.colorbar(im, cax=cax)
            spec = spec.replace("_", " ")
            plt.yticks(fontsize=40)
            ax.set_title('%s prediction map' % spec, fontsize=80)
            spec = spec.replace(" ", "_")
            plt.savefig(self.ch.result_path + '/{}/{}_predicted_map_color.png'.format(spec, spec), dpi=my_dpi)
