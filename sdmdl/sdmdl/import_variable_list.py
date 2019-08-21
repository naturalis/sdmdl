def import_variable_list(path):
    
    var_names = open(path+"/data/gis/stack/variable_list.txt")
    var_names = var_names.read()
    var_names = var_names.split("\n")
    scaled_len = int(var_names[-1])
    var_names = var_names[0:-1]
    var_len = len(var_names)
    
    return(var_names,scaled_len,var_len)