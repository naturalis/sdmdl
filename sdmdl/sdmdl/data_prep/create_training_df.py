import pandas as pd
import gdal
import numpy as np
import os
import rasterio


class CreateTrainingDF:

    def __init__(self,oh,gh,ch,verbose):
        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def prep_training_df(self,src,inRas,i):
        data = pd.read_csv(self.gh.spec_ppa + '/%s_ppa_dataframe.csv' % i)
        spec = data["taxon_name"][0]
        spec = spec.replace(" ", "_")
        len_pd = np.arange(len(data))
        long = data["dLon"]
        lati = data["dLat"]
        ppa = data["present/pseudo_absent"]
        lon = long.values
        lat = lati.values
        row = []
        col = []
        for i in len_pd:
            row_n, col_n = src.index(lon[i], lat[i])
            row.append(row_n)
            col.append(col_n)
        myarray = inRas.ReadAsArray()
        mean_std = pd.read_csv(self.gh.gis + '/env_bio_mean_std.txt', sep="\t")
        mean_std = mean_std.to_numpy()
        return(spec,ppa,long,lati,row,col,myarray,mean_std)

    def create_training_df(self):
        src = rasterio.open(self.gh.stack + '/stacked_env_variables.tif')
        inRas = gdal.Open(self.gh.stack + '/stacked_env_variables.tif')
        for i in self.oh.name:
            spec, ppa, long, lati, row, col, myarray, mean_std = self.prep_training_df(src,inRas,i)
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