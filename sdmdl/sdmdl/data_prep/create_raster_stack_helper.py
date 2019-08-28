import earthpy.spatial as es
import os

class create_raster_stack_helper():

    def __init__(self, oh, gh, ch, verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def path_exists(self):
        if not os.path.isdir(self.gh.stack):
            os.makedirs(self.gh.stack, exist_ok=True)

    def create_raster_stack(self):
        if self.verbose:
            print('Creating raster stack' + (29 * ' ') + ':', end='')
        self.path_exists()
        es.stack(self.gh.variables, self.gh.stack + '/stacked_env_variables.tif')
        if self.verbose:
            print(' Done!', end='\n')

