import earthpy.spatial as es
import os
import tqdm


# Why is this not called RasterStack?
# What does this class do?
class RasterStack():

    # Why does this again have the same constructor? 
    # This should use inheritance.
    def __init__(self, gh, verbose):
        self.gh = gh
        self.verbose = verbose

    def create_raster_stack(self):

        for once in tqdm.tqdm([0], desc='Creating raster stack' + (29 * ' ')) if self.verbose else [0]:
            if not os.path.isdir(self.gh.stack):
                os.makedirs(self.gh.stack, exist_ok=True)
            es.stack(self.gh.variables, self.gh.stack + '/stacked_env_variables.tif')
