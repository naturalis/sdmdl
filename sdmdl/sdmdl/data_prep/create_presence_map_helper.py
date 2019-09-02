import pandas as pd
import rasterio
import tqdm
import os


class CreatePresenceMapHelper:
    # What is this class? Why is it not called PresenceMap? Why is 
    # this object called a verb, and not a noun?

    # what are oh, gh, ch, verbose? When you make the constructor,
    # you write then and there what the arguments are. Not afterwards.
    def __init__(self, oh, gh, ch, verbose):
        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose
        self.map_coords = []

    def open_band(self):
        src = rasterio.open(self.gh.empty_map)
        profile = src.profile
        band = src.read(1)
        new_band = band.copy()

        return src, profile, new_band

    def confirm_path(self):
        if not os.path.isdir(self.gh.presence):
            os.makedirs(self.gh.presence, exist_ok=True)

    # Why are dictionary keys hardcoded in here? What do they mean?
    def extract_lat_lon(self, key):
        presence_data = self.oh.spec_dict[key]
        presence_data["present/pseudo_absent"] = 1
        long = presence_data["dLon"]
        lati = presence_data["dLat"]
        lon = pd.Series.tolist(long)
        lat = pd.Series.tolist(lati)
        return presence_data, lon, lat

    def convert_spatial_to_image(self, presence_data, src, lat, lon, new_band):
        for i in range(0, len(presence_data)):
            row, col = src.index(lon[i], lat[i])
            self.map_coords += [[row, col]]
            new_band[row, col] = 1
        return new_band

    def create_presence_maps(self):
        src, profile, new_band = self.open_band()
        self.confirm_path()

        for key in tqdm.tqdm(self.oh.spec_dict, desc='Creating presence maps' + (28 * ' ')):
            presence_data, lon, lat = self.extract_lat_lon(key)
            new_band = self.convert_spatial_to_image(presence_data, src, lat, lon, new_band)

            with rasterio.open(self.gh.presence + '/%s_presence_map.tif' % key, 'w', **profile) as dst:
                dst.write(new_band.astype(rasterio.float32), 1)
