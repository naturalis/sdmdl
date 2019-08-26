import earthpy.spatial as es
import os


class create_raster_stack_helper():

    def __init__(self, oh, gh, ch, verbose):

        self.oh = oh
        self.gh = gh
        self.ch = ch
        self.verbose = verbose

    def print_start(self):
        if self.verbose:
            print('Creating raster stack' + (29 * ' ') + ':', end='')

    def path_exists(self):
        if not os.path.isdir(self.gh.stack):
            os.makedirs(self.gh.stack, exist_ok=True)

    def print_end(self):
        if self.verbose:
            print(' Done!', end='\n')

    def create_raster_stack(self):
        self.print_start()
        self.path_exists()
        es.stack(self.gh.variables, self.gh.stack + '/stacked_env_variables.tif')
        self.print_end()
