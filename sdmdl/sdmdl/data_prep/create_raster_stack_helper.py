import earthpy.spatial as es
import os

# Why is this not called RasterStack?
# What does this class do?
class CreateRasterStackHelper():

    # Why does this again have the same constructor? 
    # This should use inheritance.
    def __init__(self, oh, gh, ch, verbose):
        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def create_raster_stack(self):
        
        # Why are we not using logging?
        if self.verbose:
            print('Creating raster stack' + (29 * ' ') + ':', end='')
        if not os.path.isdir(self.gh.stack):
            os.makedirs(self.gh.stack, exist_ok=True)
        es.stack(self.gh.variables, self.gh.stack + '/stacked_env_variables.tif')
        if self.verbose:
            print(' Done!', end='\n')

