import earthpy.spatial as es
import os
    
def create_raster_stack(path,verbose = True):
    
    if verbose:
        print('Creating raster stack:',end='')
    
    # variables_list function that collects all .tif files in a specific folder.
    
    def variables_list (path):
        f = []
        n = []
        for a, b, c in os.walk(path):
            for file in c:
                if file.endswith('.tif') and "stacked" not in file:
                    f += [a.replace('\\','/') + '/' + file]
                    n += [file.replace('.tif','')]
        return([f,n])
        
    # Create a scaled and non-scaled variable list.
        
    variables_s, names_s = variables_list(path + '/data/gis/layers/scaled')
    vsl = len(variables_s)
    variables_ns, names_ns = variables_list(path + '/data/gis/layers/non-scaled')
    
    # Merge lists with scaled variables first.
    
    variables = variables_s + variables_ns
    names = names_s + names_ns
    
    # When stack folder does not exist create it.
    
    if not os.path.isdir(path+'/data/GIS/stack'):
        os.makedirs(path+'/data/GIS/stack',exist_ok=True)
     
    es.stack(variables, path+"/data/GIS/stack/stacked_env_variables.tif")
    
    # Save the names of the variables to list.
    
    myfile = open(path+'/data/GIS/stack/variable_list.txt', 'w+')
    for item in names:
        myfile.write(item+"\n")
    myfile.write(str(vsl))
    myfile.close()
    
    if verbose:
        print(' Done!')