import earthpy.spatial as es
import os
import tqdm


class RasterStack:

    """Stacks all raster files detected by GIS object (gh) into a single raster stack (.tif) file. This procedure is
    only successful if all detected environmental layers have identical affine transformation and resolution.
    WARNING: the file 'empty_land_map.tif' in 'root/data/gis/layers' needs to have the same affine transformation and
    resolution as all other raster files provided, as presence maps are create using this file as a template.
    This currently makes it impossible to use other environmental layers without transforming them to have the same
    affine projection and coordinate system as 'empty_land_map.tif' (or vice versa).

    :param gh: a GIS object: holds path and file names required for computation of gis data.
    :param verbose: a boolean: prints a progress bar if True, silent if False

    :return: Object. Used to stack all provided environmental layers into one single object that is subsequently written
    to a raster (.tif) file. Performed by calling class method create_raster_stack on RasterStack object.
    """

    def __init__(self, gh, verbose):
        self.gh = gh
        self.verbose = verbose

    def create_raster_stack(self):

        """Stacks all provided raster files by the GIS object (gh) into a single raster stack, where each band
        corresponds to one environmental variable.

        :param self: a class instance of RasterStack

        :return: None. Does not return value or object, instead writes away the raster stack to a new (.tif) file.
        """

        for _ in tqdm.tqdm([0], desc='Creating raster stack' + (29 * ' ')) if self.verbose else [0]:
            if not os.path.isdir(self.gh.stack):
                os.makedirs(self.gh.stack, exist_ok=True)

            # WARNING: this can cause errors if raster layers with different affine transformations / spatial extent or
            # resolutions are detected and used by the model, THIS ALSO INCLUDES THE FILE 'empty_land_map.tif'. This
            # means that the input raster files should match the spatial extent (Longitude_max = 180, Longitude_
            # min = -180, Latitude_max = 90, Latitude_min = -60) of the already existing 'empty_land_map.tif' included
            # in the repository. Alternatively the included 'empty_land_map.tif' can be edited to match the spatial
            # extent of the users raster files.

            es.stack(self.gh.variables, self.gh.stack + '/stacked_env_variables.tif')
