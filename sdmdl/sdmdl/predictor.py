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

# Give more options to control predictor class, e.g. options to only output one file type (raster layer or image)

class Predictor:
    """Manages all aspects of the prediction process. E.g. loading the prediction dataset, performing predictions,
    creating visuals and saving the resulting distribution map as a raster layer.

    :param oh: an Occurrence object: holds occurrence files and tables
    :param gh: a GIS object: holds path and file names required for computation of gis data.
    :param ch: a Config object: holds instance variable for result path.
    :param verbose: a boolean: prints a progress bar if True, silent if False

    :return: Object. Used to create species distribution maps, these maps are saved in two formats:
    1. A raster (.tif) file that can be easily used in other analyses
    2. A visualization (.png) file with a simple title, prediction map and legend.
    Performed by calling class method predict_model on Predictor object.
    """

    def __init__(self, oh, gh, ch, verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def prep_color_scheme(self):

        """Setup plot colors and settings

        :return: LinearSegmentedColormap. Object that manages the colors of the legend in the visualized map output.
        """

        norm = matplotlib.colors.Normalize(0, 1)

        # To Do: integrate color scheme (potentially as a list [col1, col2, col3, coln]) into the config file.
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

        """Loads raster stack and empty map

        :return: Tuple. Containing:
        matrix 'myarray' a multi-dimensional matrix representation of the raster stack;
        matrix 'index_minb1' an array of x, y coordinates masking the locations of NoData (or non-terrestrial) values in
        the empty land map
        """

        inRas = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        myarray = inRas.ReadAsArray()
        src = rasterio.open(self.gh.empty_map)
        b = src.read(1)
        minb = np.min(b)
        index_minb1 = np.where(b == minb)
        return myarray, index_minb1

    def predict_distribution(self, species, myarray, index_minb1):

        """Predicts the presence or absence of a species globally, using the world_prediction_array.npy as input to the
        model.

        :param species: String representation of species name
        :param myarray: a multi-dimensional matrix representation of the raster stack
        :param index_minb1: an array of x, y coordinates masking the locations of NoData (or non-terrestrial) values in
        the empty land map

        :return: Tuple. Containing:
        matrix 'new_band' is a two dimensional matrix holding the values predicted by the model for each (x, y) location
        """

        spec = species
        spec_index = self.gh.names.index("%s_presence_map" % spec)
        input_X = np.load(self.gh.gis + '/world_prediction_array.npy')
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
        row = df["row"]
        row = row.values
        col = df["col"]
        col = col.values
        for i in range(0, len(row)):
            new_band[int(row[i]), int(col[i])] = new_band_values[i]
        new_band[index_minb1] = np.nan
        return new_band

    def predict_model(self):

        """Manages the entire prediction process from beginning to end by calling class methods. Finishes with
        plotting a map visualization with a title and legend.

        :return: None. Does not return value or object, instead plots one map per species using matplotlib and saves the
        prediction data to a raster file.
        """

        custom_cmap = self.prep_color_scheme()
        myarray, index_minb1 = self.prep_prediction_data()
        for species in tqdm.tqdm(self.oh.name,
                                 desc='Predicting globally' + (31 * ' '), leave=True) if self.verbose else self.oh.name:
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
