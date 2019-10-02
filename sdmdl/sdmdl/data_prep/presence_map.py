import pandas as pd
import rasterio
import tqdm
import os


# PresenceMap could include functionality on creating the empty map from scratch.
# This would require parameters in the config file for resolution and affine projection / spatial extent
# The empty land map raster can be generated from a simple shapefile (which could potentially be obtained from a remote
# location, so it will not have to be included in the data folder).

class PresenceMap:

    """Creates a presence map (.tif) for each species in the occurrence object (oh)
    by using an empty land map raster layer and changing the value of any occurrence locations to 1.
    Note: the empty land map (found in 'root/data/gis/layers') needs to have the same affine transformation and
    resolution as all other raster layers used during the data preparation process, if this is not the case this will
    lead to problems when creating the raster stack (see raster_stack.py).

    :param oh: an Occurrence object: holds occurrence files and tables
    :param gh: a GIS object: holds path and file names required for computation of gis data.
    :param verbose: a boolean: prints a progress bar if True, silent if False

    :return: Object. Used to create presence maps raster (.tif) files containing presence maps for each occurrence
    species. Performed by calling class method create_presence_map on PresenceMap object.
    """

    def __init__(self, oh, gh, verbose):
        self.oh = oh
        self.gh = gh
        self.verbose = verbose

    def create_presence_map(self):

        """Loads a copy of the empty land map for each species and sets the locations of occurrences to 1,
        saves one presence map per species detected by the Occurrence (oh) object.

        :param self: a class instance of PresenceMap

        :return: None. Does not return value or object, instead writes one raster file .tif for each species detected
        by Occurrences. The created maps contain three distinct values: No data for any pixels representing
        non-terrestrial locations, 0 for any pixels representing terrestrial locations with no occurrence(s) and 1
        representing pixels with an occurrence.
        """

        src = rasterio.open(self.gh.empty_map)
        profile = src.profile
        band = src.read(1)
        if not os.path.isdir(self.gh.presence):
            os.makedirs(self.gh.presence, exist_ok=True)
        for key in tqdm.tqdm(self.oh.spec_dict, desc='Creating presence maps' + (28 * ' '), leave=True) if self.verbose else self.oh.spec_dict:
            new_band = band.copy()
            presence_data = self.oh.spec_dict[key]

            # dictionary keys used for querying tables from spec_dict. the columns of these tables are set by the
            # occurrence class so are not define by the user.
            presence_data["present/pseudo_absent"] = 1
            long = presence_data["dLon"]
            lati = presence_data["dLat"]
            lon = pd.Series.tolist(long)
            lat = pd.Series.tolist(lati)
            for i in range(0, len(presence_data)):
                row, col = src.index(lon[i], lat[i])
                new_band[row, col] = 1
            with rasterio.open(self.gh.presence + '/%s_presence_map.tif' % key, 'w', **profile) as dst:
                dst.write(new_band.astype(rasterio.float32), 1)
