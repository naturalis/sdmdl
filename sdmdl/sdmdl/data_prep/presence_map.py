import pandas as pd
import rasterio
import tqdm
import os


class PresenceMap:
    # What is this class? Why is it not called PresenceMap? Why is 
    # this object called a verb, and not a noun?

    # what are oh, gh, ch, verbose? When you make the constructor,
    # you write then and there what the arguments are. Not afterwards.
    def __init__(self, oh, gh, verbose):
        self.oh = oh
        self.gh = gh
        self.verbose = verbose

    def create_presence_map(self):
        src = rasterio.open(self.gh.empty_map)
        profile = src.profile
        band = src.read(1)
        new_band = band.copy()
        if not os.path.isdir(self.gh.presence):
            os.makedirs(self.gh.presence, exist_ok=True)
        for key in tqdm.tqdm(self.oh.spec_dict, desc='Creating presence maps' + (28 * ' '), leave=True) if self.verbose else self.oh.spec_dict:
            presence_data = self.oh.spec_dict[key]
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
